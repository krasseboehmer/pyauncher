# Pyauncher

A simple and lightweight application launcher for Linux desktops.

![Pyauncher Screenshot](./pics/interface.png)

## Features

*   **Instant Search:** Find applications as you type.
*   **Keyboard Navigation:** Navigate the application list with arrow keys.
*   **Launch with Enter:** Press Enter to launch the selected application.
*   **Top of the Screen:** Appears at the top of the screen for easy access.
*   **Modern Look:** Rounded corners and a clean, dark theme.
*   **Lightweight:** Minimal dependencies and resource usage.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3
*   pip

## Installation

To install Pyauncher as a desktop application, follow these steps:

1.  **Clone the repository and navigate to the project directory:**
    ```bash
    git clone https://github.com/krasseboehmer/pyauncher.git
    cd pyauncher
    ```

2.  **Run the installation script:**
    ```bash
    ./install.sh
    ```

3.  **You can now launch Pyauncher from your application menu.**

## Usage

The recommended way to run Pyauncher is by using the provided `launch.sh` script, which automatically handles the virtual environment.

### Launching with `launch.sh`

To run the application using the `launch.sh` script, simply execute it from the project root:

```bash
./launch.sh
```

This script will automatically use the Python interpreter from the `venv` directory to run `main.py`.

### Launching by activating the virtual environment (Alternative)

If you prefer to activate the virtual environment manually, you can do so with the following commands:

```bash
source venv/bin/activate
python3 main.py
```

You can also create a desktop shortcut or a keybinding in your display manager to launch the application more easily.

## Uninstall

To uninstall Pyauncher, run the `uninstall.sh` script from the project directory:

```bash
./uninstall.sh
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
