# Assignment 2
### Roll Number: 2024101096

## How To Run

### 1) Setup

From project root:

```bash
python -m pip install -U pytest
```

### 2) Run The Code

Whitebox app:

```bash
python whitebox/code/main.py
```

Integration app:

```bash
python integration/code/main.py
```

### 3) Run The Tests

Whitebox tests (recommended):

```bash
pytest -q whitebox/tests/test_whitebox.py
```

Whitebox tests (direct script mode):

```bash
cd whitebox/tests
python test_whitebox.py
```

Integration tests (recommended):

```bash
python -m integration.tests.test_all
```

Integration tests (direct script mode):

```bash
cd integration/tests
python test_all.py
```

Blackbox tests:

```bash
pytest -q blackbox/tests
```

Note:
- Some blackbox tests may require the target backend service to be running first.

Github Repo Link: https://github.com/flakes22/dass_testing.git
OneDrive Link: https://iiithydstudents-my.sharepoint.com/:u:/g/personal/mahek_desai_students_iiit_ac_in/IQB57pTKErCRTpwi_c5HHdIgAaFo3QmY1kg6nOyso3q3vVI?e=cTNX6E
