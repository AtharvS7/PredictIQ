"""Portable container entry point; honors the hosting provider's assigned port."""
import os

import uvicorn


def port_from_environment():
    port = int(os.environ.get('PORT', '8000'))
    if not 1 <= port <= 65535:
        raise ValueError('PORT must be between 1 and 65535')
    return port


if __name__ == '__main__':
    # One API process until rate-limit state is shared across workers/replicas.
    uvicorn.run('main:app', host='0.0.0.0', port=port_from_environment(),
                workers=1, access_log=False)
