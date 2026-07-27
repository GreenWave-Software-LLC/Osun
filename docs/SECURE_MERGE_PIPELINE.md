# Secure merge pipeline

**Workflow:** `.github/workflows/merge-gate.yml`

**Required check:** `Merge gate passed`

**Events:** pull requests to `main`, merge queue groups, pushes to `main`, and manual dispatch

## What the gate enforces

Every candidate runs:

1. the full Python suite on Python 3.11 and 3.13 with `ResourceWarning` treated as an error;
2. Python bytecode compilation, browser JavaScript syntax validation, and patch-format validation;
3. the local repository security-invariant scanner;
4. Bandit static security analysis at medium/high severity;
5. `pip-audit` against project dependency metadata.

The workflow has read-only repository permissions, persists no checkout credential, passes no repository secrets to pull-request code, and pins every external action to a full commit SHA. Dependabot proposes updates for action and Python security-tool versions.

The local invariant scanner rejects common committed credential formats, private-key containers, mutable action references, `pull_request_target`, broad write permissions, and removal of core merge controls. It complements provider-side secret scanning; it is not a substitute for Home Assistant token revocation or GitHub Secret Protection.

## Required GitHub ruleset

A workflow file reports checks but cannot prevent an administrator from pushing directly. In **Repository Settings → Rules → Rulesets**, create or update the active ruleset targeting `main` with:

- require a pull request before merging;
- require status checks to pass and select **Merge gate passed**;
- require the branch to be up to date before merging;
- block force pushes and branch deletion;
- do not allow bypass except explicit repository emergency administration.

If GitHub merge queue is enabled later, the workflow already handles `merge_group` and the same required check.

Workflow or ruleset changes are security-boundary changes. They require deliberate owner review even when the gate itself is green. For stronger separation as more collaborators join, move this gate into an organization-required workflow and require CODEOWNERS review for `.github/**`, `scripts/security_gate.py`, and this policy.

## Local reproduction

```powershell
$env:PYTHONPATH = "src"
python -W error::ResourceWarning -m unittest discover -s tests -v
node --check src/osun/web/app.js
python scripts/security_gate.py
python -m bandit -q -r src -ll
python -m pip_audit --progress-spinner off .
git show --check --format= HEAD
```

Install the last two tools into an isolated environment from `requirements-security.txt`; they are CI tooling, not Osun runtime dependencies.
