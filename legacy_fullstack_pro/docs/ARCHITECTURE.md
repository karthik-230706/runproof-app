# RunProof Architecture

```text
User
  │
  ├── Web Dashboard
  └── CLI
       │
       ▼
Backend API / Session / Storage
       │
       ▼
RunProof Core Engine
  ├── Scanner
  ├── Detector
  ├── Runtime + Tool Checker
  ├── Dependency Analyzer
  ├── Environment Analyzer
  ├── Security Static Checks
  ├── Safe Execution Policy
  ├── Build/Test Engine
  ├── Readiness Scoring
  ├── RunProof Doctor
  ├── Double-Build Verifier
  ├── SHA-256 Fingerprinting
  ├── Passport + Signature
  ├── Dependency Inventory
  └── Evidence Bundle
```

## Two separate results

RunProof deliberately separates:

1. **Reproducibility Readiness Score** — static/runtime/build/test readiness.
2. **Verified Reproducibility** — only after two isolated builds create matching configured artifacts.

This prevents a misleading "100% reproducible" claim based only on one successful run.
