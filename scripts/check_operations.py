"""Bounded read-only liveness/readiness monitoring and light load acceptance.

Never exercises writes or sends credentials. Redirects are rejected. This is a
small operational smoke check, not a capacity benchmark or denial-of-service test.
"""
import argparse
import concurrent.futures
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def api_base(value):
    parsed = urllib.parse.urlsplit(value)
    if (parsed.username or parsed.password or parsed.query or parsed.fragment
            or not parsed.hostname or parsed.path.rstrip('/') not in {'', '/api/v1'}):
        raise ValueError('Use an API origin or /api/v1 base without credentials or query parameters')
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in {'127.0.0.1', 'localhost', '::1'}):
        raise ValueError('Hosted checks require HTTPS')
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, '/api/v1', '', ''))


def probe(base, route, timeout):
    started = time.monotonic()
    status, healthy, error_type = None, False, None
    try:
        opener = urllib.request.build_opener(NoRedirect)
        request = urllib.request.Request(base + '/' + route, headers={'User-Agent': 'PredictIQ-Operations/1'})
        with opener.open(request, timeout=timeout) as response:
            status = response.status
            payload = response.read(65537)
            if len(payload) > 65536:
                raise ValueError('Oversized health response')
            body = json.loads(payload)
            expected = 'alive' if route == 'live' else 'healthy'
            healthy = status == 200 and isinstance(body, dict) and body.get('status') == expected
            if route == 'ready' and healthy:
                services = body.get('services', {})
                mode = body.get('release_mode', 'prediction')
                if mode == 'manual_budget':
                    capabilities = body.get('capabilities', {})
                    healthy = (services.get('database') == 'connected' and services.get('firebase') == 'initialized'
                               and services.get('ml_model') in {'ready', 'not_loaded'}
                               and capabilities.get('manual_budget') is True
                               and capabilities.get('automatic_prediction') is (services.get('ml_model') == 'ready'))
                else:
                    healthy = mode == 'prediction' and services == {'database': 'connected', 'ml_model': 'ready', 'firebase': 'initialized'}
    except urllib.error.HTTPError as error:
        status, error_type = error.code, 'HTTPError'
    except Exception as error:
        error_type = type(error).__name__
    return {'route': route, 'status': status, 'healthy': healthy, 'error_type': error_type,
            'latency_ms': round((time.monotonic() - started) * 1000, 2)}


def check(base, requests=2, concurrency=1, timeout=10.0, max_p95_ms=10000.0):
    base = api_base(base)
    if not 2 <= requests <= 100 or not 1 <= concurrency <= 4 or not 0 < timeout <= 30 or not 0 < max_p95_ms <= 30000:
        raise ValueError('Checks require 2-100 requests, 1-4 workers and bounded positive deadlines')
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(probe, base, 'live' if i % 2 == 0 else 'ready', timeout)
                   for i in range(requests)]
        samples = [future.result() for future in futures]
    summaries = {}
    for route in ('live', 'ready'):
        subset = [sample for sample in samples if sample['route'] == route]
        durations = sorted(sample['latency_ms'] for sample in subset)
        summaries[route] = {'requests': len(subset), 'failures': sum(not sample['healthy'] for sample in subset),
                            'p95_ms': durations[math.ceil(len(durations) * .95) - 1],
                            'max_ms': max(durations)}
    passed = all(s['failures'] == 0 and s['p95_ms'] <= max_p95_ms for s in summaries.values())
    return {'status': 'passed' if passed else 'failed', 'checks': summaries,
            'concurrency': concurrency, 'max_p95_ms': max_p95_ms, 'samples': samples}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--requests', type=int, default=2)
    parser.add_argument('--concurrency', type=int, default=1)
    parser.add_argument('--timeout', type=float, default=10)
    parser.add_argument('--max-p95-ms', type=float, default=10000)
    args = parser.parse_args()
    try:
        report = check(args.base_url, args.requests, args.concurrency, args.timeout, args.max_p95_ms)
        print(json.dumps(report, indent=2))
        raise SystemExit(0 if report['status'] == 'passed' else 1)
    except Exception as error:
        print(json.dumps({'status': 'failed', 'error_type': type(error).__name__}))
        raise SystemExit(1) from None
