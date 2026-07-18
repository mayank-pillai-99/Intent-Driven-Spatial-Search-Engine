# VISRI Server Setup Guide

This guide contains the commands required to run the Final Ubuntu notebook on the server and access the VISRI Gradio application.

---

## 1. Connect to the server

From your local machine terminal:

```bash
ssh -L 8890:localhost:8890 <your_username>@<server_ip>
```

---

## 2. Start the database container and launch Jupyter

Run on the server:

```bash
docker start visri_postgis
source ~/visri_ubuntu_env/bin/activate
cd ~/VISRI_Mayank_Pillai
jupyter notebook --no-browser --port=8890
```

Open the printed URL in your browser on your local machine (for example `http://localhost:8890/?token=...`).

---

## 3. Open the notebook

In the Jupyter interface, open:

```text
notebooks/Final Ubuntu.ipynb
```

Run all cells.

---

## 4. Access the VISRI Web Interface

Once all notebook cells have finished executing and the Gradio application has started, users connected to the same university network/Wi-Fi can access the application using:

```text
http://172.24.16.136:7860
```

**Notes:**

- The notebook must remain running for the web interface to stay available.
- Users must be connected to the same university network (or VPN, if applicable).
- If the notebook is stopped, the web interface will no longer be accessible.

---

## 5. Stop the notebook server and Docker container when done

In the terminal where Jupyter is running, press:

```bash
Ctrl+C
```

Then deactivate the environment if needed:

```bash
deactivate
```

To stop the Docker container:

```bash
docker stop visri_postgis
```

To start it again later, use:

```bash
docker start visri_postgis
```