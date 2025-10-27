# Stacktape Deployment Issue

## Problem

Stacktape's `stacktape-lambda-buildpack` for Python has **mandatory code minification** using `python-minifier`, which fails on modern Pydantic (v2.x) syntax.

### Error Details

```
python_minifier.UnstableMinification: Minification was unstable!
File: ./pydantic/fields.py
Syntax Error: else:return Annotated[A.annotation,*A.metadata]
                                                ^
SyntaxError: invalid syntax
```

The issue is that `python-minifier` doesn't support Python 3.9+ unpacking syntax (`*args`) in type annotations, which Pydantic 2.x heavily uses.

## Root Cause

- Stacktape's buildpack uses **Python 3.9-alpine** Docker image for building
- The buildpack **mandatorily minifies** all Python code (no opt-out option)
- `PyLanguageSpecificConfig` has no `minify: false` option (only: `packageManager`, `packageManagerFile`, `pythonVersion`, `runAppAs`)
- Modern frameworks like FastAPI + Pydantic v2.x are incompatible with `python-minifier`

## Attempted Solutions

1. ❌ **Disable minification** - No such option exists in Stacktape
2. ❌ **Use `stacktape-image-buildpack`** - Not valid for Lambda functions
3. ❌ **Use `custom-artifact` with Dockerfile** - Requires pre-built package, not supported
4. ❌ **Exclude pydantic files** - Would break FastAPI (hard dependency)
5. ❌ **Language-specific config** - No minification control available

## Solutions

### Option 1: Contact Stacktape Support ⭐ RECOMMENDED

Ask Stacktape to add `minify: false` option to `PyLanguageSpecificConfig`:

```yaml
packaging:
  type: stacktape-lambda-buildpack
  properties:
    entryfilePath: lambda_handler.py
    languageSpecificConfig:
      minify: false  # <-- Not currently supported
```

**Discord**: https://discord.gg/gSvzRWe3YD

### Option 2: Use AWS SAM/CDK Directly

Deploy using AWS SAM or CDK instead of Stacktape:

```bash
# Install AWS SAM CLI
brew install aws-sam-cli

# Deploy
sam build
sam deploy --guided
```

The [Dockerfile.lambda](Dockerfile.lambda) is already prepared for this approach.

### Option 3: Use Serverless Framework

Serverless Framework doesn't minify Python by default:

```bash
npm install -g serverless
serverless deploy
```

### Option 4: Downgrade Pydantic (NOT RECOMMENDED)

Downgrade to Pydantic v1.x (loses type safety, modern features):

```bash
pip install "pydantic<2.0"
```

## Current Status

- ✅ All code is ready for AWS Lambda deployment
- ✅ [lambda_handler.py](lambda_handler.py) configured with Mangum
- ✅ [Dockerfile.lambda](Dockerfile.lambda) created for container-based deployment
- ✅ [stacktape.yml](stacktape.yml) configured (blocked by minification issue)
- ⏳ **Blocked**: Waiting for Stacktape minification workaround

## Recommendation

**Contact Stacktape support** to request a `minify: false` option for Python Lambda functions. This is a common requirement for modern Python frameworks (FastAPI, Pydantic v2, etc.).

In the meantime, you can:
1. Deploy to Vercel (currently working)
2. Use AWS SAM/CDK for Lambda deployment
3. Use Serverless Framework

Once Stacktape adds the minification opt-out, deployment will work with the existing [stacktape.yml](stacktape.yml) configuration.
