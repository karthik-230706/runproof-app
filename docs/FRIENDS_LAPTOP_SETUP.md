# Open RunProof on a Friend's Laptop

## Same Wi-Fi

RunProof V3 uses:

```text
RUNPROOF_HOST=0.0.0.0
```

Start RunProof. The terminal prints two addresses, for example:

```text
This laptop : http://127.0.0.1:8000
Same Wi-Fi  : http://192.168.1.24:8000
```

Your friend should open the **Same Wi-Fi** address, not `127.0.0.1`.

Both laptops normally need to be connected to the same Wi-Fi/network.

If Windows Firewall asks about Python, allow it on **Private networks**.

You can also open RunProof → Security Center → Other Laptop Access to see the address.

## Different Wi-Fi / different city

A local Flask server is not a public website. For access from anywhere, deploy RunProof behind HTTPS on a proper hosting/server platform.

Do not expose the development server directly to the public internet, especially when project uploads are enabled.
