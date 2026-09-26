"""The code side: a package's public API, read from source with the ast module.

Every public function, class (its constructor's parameters) and public method, keyed by a
stable id (module path plus qualified name), with its parameter names."""
import ast


def params(fn):
    a = fn.args
    return [x.arg for x in a.posonlyargs + a.args + a.kwonlyargs if x.arg not in ("self", "cls")]


def public(name):
    return not name.startswith("_")


def api(source, module):
    """{id: [parameter names]} for one module's source; {} if it does not parse."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and public(node.name):
            out[f"{module}:{node.name}"] = params(node)
        elif isinstance(node, ast.ClassDef) and public(node.name):
            init = next((n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"), None)
            out[f"{module}:{node.name}"] = params(init) if init else []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and public(item.name):
                    out[f"{module}:{node.name}.{item.name}"] = params(item)
    return out


def short(item_id):
    """The name a doc calls it by: the class for a constructor, the method name for a method."""
    return item_id.split(":", 1)[1].split(".")[-1]


def changes(before, after):
    """Signature changes between two API snapshots (several modules merged). An item that leaves one
    module and appears under the same name in another has moved, not gone."""
    out = []
    after_names = {short(k) for k in after}
    for k, old in before.items():
        if k not in after:
            if short(k) not in after_names:
                out.append({"item": k, "kind": "removed"})
            continue
        new = after[k]
        gone, added = [p for p in old if p not in new], [p for p in new if p not in old]
        for p in gone:
            out.append({"item": k, "kind": "parameter removed", "param": p,
                        "renamed_to": added[0] if len(gone) == 1 and len(added) == 1 else None})
        for p in added:
            if not (len(gone) == 1 and len(added) == 1):
                out.append({"item": k, "kind": "parameter added", "param": p})
    return out
