import logging
import os
from math import floor

from .helper import get_savedvarsdir


def _sv_parser(path):
    try:
        with open(path, "r") as f:
            lua = f.read()

        """
        bring lua saved-var file into a useable format:
        - one line per expression (add \n where needed)
        - remove all redundant characters
        - make lowercase, split into list of expressions
        - remove empty expressions
        EXPRESSIONS: A) List-Start "name=", B) Variable assignment "name=val", C) List End "}"
        """
        subs = ((",", "\n"), ("{", "{\n"), ("}", "}\n"),
                ("{", ""), (",", ""), ("[", ""), ("]", ""), ('"', ""), (" ", ""))
        for old, new in subs:
            lua = lua.replace(old, new)
        lua = lua.lower().split("\n")
        lua = [expression for expression in lua if expression]

        """
        the lua saved-var file is parsed to a tree of dicts
        each line represents either one node in the tree or the end of a subtree
        the last symbol of each line decides the type of the node (branch vertex or leaf)
        """
        stack = []
        root = (dict(), "root")
        stack.append(root)
        for line in lua:
            if line == "":
                break
            if line[-1] == '=':  # subtree start
                t = dict()
                tname = line.split("=")[0]
                stack.append((t, tname))
            elif line[-1] == '}':  # subtree end
                t = stack.pop()
                tp = stack.pop()
                tp[0][t[1]] = t[0]
                stack.append(tp)
            else:  # new element in tree
                name, val = line.split("=")
                t = stack.pop()
                t[0][name] = val
                stack.append(t)
        return root[0]

    except Exception as ex:
        logging.error("Error: '" + str(ex) + "' occured, while parsing ESO variables.")
        return None


def sv_color_extract(Colors):
    root = _sv_parser(os.path.join(get_savedvarsdir(), "Chalutier.lua"))
    if root is None:
        return Colors

    for i in range(4):
        name, root = root.popitem()
    colors = []
    for i in root["colors"]:
        """
        ingame representation of colors range from 0 to 1 in float
        these values are scaled by 255
        """
        rgb = [
            floor(float(root["colors"][i]["r"]) * 255),
            floor(float(root["colors"][i]["g"]) * 255),
            floor(float(root["colors"][i]["b"]) * 255)
        ]
        colors.append(rgb)
    for i, c in enumerate(Colors):
        Colors[c] = colors[i]
    return Colors
