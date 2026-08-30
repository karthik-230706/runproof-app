# First — Update to V3 Correctly

Use these steps before changing any more code.

## 1. Stop the old RunProof
Go to the old VS Code terminal and press:

```text
Ctrl + C
```

## 2. Keep the old folder
Do not delete it yet. It is your backup.

## 3. Extract the new V3 ZIP
You will get:

```text
RunProof_Ultimate_v3
```

## 4. Open ONLY that inner V3 folder in VS Code
You should see:

```text
backend
frontend
demo
docs
START_RUNPROOF.bat
requirements.txt
run.py
```

## 5. Easiest start
Double-click:

```text
START_RUNPROOF.bat
```

It handles the virtual environment and packages for you.

## 6. Open the site
Use:

```text
http://127.0.0.1:8000
```

## 7. For real phone OTP
Before testing real SMS, complete `docs/REAL_OTP_SETUP.md`.

## 8. For a friend's laptop
Use the `Same Wi-Fi` address printed when RunProof starts, or open Security Center → Other Laptop Access.

## 9. Test all important UI controls
Check:

- project name opens
- Projects card opens Workspace
- Verified card opens Verifications
- Need Attention opens Doctor
- sun/moon changes theme
- bell opens notifications
- avatar opens profile menu
- Ctrl+K opens search
- Team invite stores an invite
- Developer Settings creates/revokes a token
- RunProof Guide answers app questions
- Passports and Reports show empty states or real items

## 10. Test the three proof demos

### Good Demo
Expected: VERIFIED REPRODUCIBLE

### Broken Demo
Expected: BUILD VERIFICATION FAILED

### Non-Repro Demo
Expected: NOT REPRODUCIBLE
