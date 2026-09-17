from unittest.mock import Mock

import boto3
from app.services.storage_service import S3StorageBackend


def test_compatible_endpoint_retains_path_and_uses_path_addressing(monkeypatch):
    factory = Mock()
    monkeypatch.setattr(boto3, 'client', factory)
    endpoint = 'https://project.storage.supabase.co/storage/v1/s3'
    S3StorageBackend('documents', 'test-region', 'fixture-access', 'fixture-secret', endpoint)
    kwargs = factory.call_args.kwargs
    assert kwargs['endpoint_url'] == endpoint
    assert kwargs['config'].s3['addressing_style'] == 'path'


def test_aws_keeps_default_endpoint_and_credential_chain(monkeypatch):
    factory = Mock()
    monkeypatch.setattr(boto3, 'client', factory)
    S3StorageBackend('documents', 'us-east-1', '', '')
    kwargs = factory.call_args.kwargs
    assert 'endpoint_url' not in kwargs
    assert 'config' not in kwargs
    assert 'aws_access_key_id' not in kwargs
