# Security and Responsible Use

This repository is an educational/research simulation. It is not certified navigation software and should not be used for safety-critical, weapon, flight-control, or operational navigation decisions.

If you identify a software security issue, open a private security advisory through GitHub rather than posting exploit details publicly.

## v0.6 integration transports

The bearer-token and TLS options in the reference gRPC transport are intended for controlled engineering environments. They do not constitute a complete production IAM, key-management, zero-trust, or safety-critical communications solution. Production deployments should use organization-approved certificate lifecycle management, secret storage, authorization policy, logging, network segmentation, and independent security review.

ROS 2 security configuration is environment-specific and is not enabled or claimed by the reference bridge.
