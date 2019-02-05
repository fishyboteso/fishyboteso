import win32gui


def config_win():
    X, Y, W, H = -8, 0, 815, 608
    hwnd = win32gui.FindWindow(None, "Elder Scrolls Online")
    win32gui.MoveWindow(hwnd, X, Y, W, H, True)


if __name__ == "__main__":
    config_win()
