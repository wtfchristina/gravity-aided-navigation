# gRPC Integration

Version 0.6 adds an optional gRPC transport for remote simulator, lab, and service integration.

Install optional dependencies:

```bash
pip install -e ".[integration]"
```

## Run the gateway

```bash
qpnt grpc-server configs/fixed_wing_fused.yaml \
  --host 127.0.0.1 \
  --port 50051 \
  --token change-me
```

Publish a synthetic scenario:

```bash
qpnt grpc-publish configs/fixed_wing_fused.yaml \
  --target 127.0.0.1:50051 \
  --token change-me
```

## Authentication

The reference implementation supports bearer-token metadata. This is intended for controlled integration environments, not as a complete enterprise identity system.

## TLS

The server can be started with a certificate and private key:

```bash
qpnt grpc-server configs/fixed_wing_fused.yaml \
  --tls-cert cert.pem \
  --tls-key key.pem
```

Clients can provide a root certificate using `--tls-root-cert`.

## Service contract

`proto/sensor_gateway.proto` supplies a typed protobuf contract that external teams may use to generate clients. The Python reference transport is protobuf wire-compatible with this contract. Runtime message classes are constructed from the same schema, so generated external clients can interoperate without checking generated Python stubs into the repository.

## Safety / scope

The gRPC transport is an engineering integration layer. It is not a certified avionics databus, safety-critical communications stack, or hardened production identity plane.
