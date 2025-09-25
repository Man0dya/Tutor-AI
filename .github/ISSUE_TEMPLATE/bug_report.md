---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

body:
  - type: textarea
    id: summary
    attributes:
      label: Summary
      description: A clear and concise description of the bug.
      placeholder: What happened?
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: Provide detailed steps to reproduce the issue.
      placeholder: 1) ... 2) ...
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
    validations:
      required: true
  - type: input
    id: frontend-version
    attributes:
      label: Frontend environment
      placeholder: OS/Browser, Node version, `client` commit
  - type: input
    id: backend-version
    attributes:
      label: Backend environment
      placeholder: OS/Python, `server` commit, Mongo/Stripe config state
  - type: textarea
    id: logs
    attributes:
      label: Relevant logs
      description: Include API stack traces or browser console logs (redact secrets).
      render: shell
  - type: checkboxes
    id: checks
    attributes:
      label: Checks
      options:
        - label: I have searched existing issues
        - label: I can reproduce this on the latest commit
