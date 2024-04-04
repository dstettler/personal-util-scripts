#!/usr/bin/env python3
import argparse
import os
import json

# Returns dictionary in the following format:
# { "using": ["std::string", "std::vector"], "content": ["all lines of content"], "includes": ["iostream", "vector", "string"] }
def processFile(headerPath: str, debug: bool) -> dict[str, list[str]]:
    final_dict = {}
    with open(headerPath, encoding='utf8') as f:
        print(f"Parsing: {headerPath}")
        content = ""
        used = []
        includes = []
        for line in f:
            line_items = line.rstrip().split(' ')

            including = False
            using = False
            define = False

            for item in line_items:
                if "#define" in item or "#ifndef" in item or "#endif" in item:
                    define = True
                    break
                elif "using" in item:
                    using = True
                    continue
                elif "#include" in item:
                    including = True
                    continue
                elif "//" in item:
                    break

                if (using):
                    split = item.split(',')
                    for split_item in split:
                        if split_item != '':
                            used.append(item.replace(";", '').replace('//', '').replace(',', ''))
                elif (including):
                    if '"' in item:
                        continue
                    includes.append(item.replace('<', '').replace('>', ''))

            if not including and not using and not define:
                content += line
        final_dict["using"] = used
        final_dict["content"] = content
        final_dict["includes"] = includes
    
    if debug:
        with open(f"dict-{headerPath.replace('/', '-')}.txt", 'w') as f:
            f.write(json.dumps(final_dict, separators=(',', ': '), sort_keys=True, indent=4))
    return final_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="cpp-compose.py", description="Uses the .cppcompose file in the target directory to generate a single C++ source file for a project"
    )

    parser.add_argument(
        "target_dir",
        metavar="target_dir",
        type=str,
        help="Directory to compose"
    )

    parser.add_argument(
        "--compose-file",
        type=str,
        help="Custom compose file location",
        required=False
    )

    parser.add_argument(
    "-d",
    action='store_true',
    help="Produce intermediary debug files",
    required=False
)
  
    args = parser.parse_args()

    target_dir = args.target_dir.rstrip("/")
    custom_compose = args.compose_file
    debug_mode = args.d

    composefile = f"{target_dir}/.cppcompose"
    if custom_compose is not None:
        composefile = custom_compose

    if not os.path.exists(target_dir):
        exit("Target directory does not exist!")

    if not os.path.exists(composefile):
        exit("Compose file does not exist!")

    read_classes: list[str] = []
    final_name: str = ""
    with open(composefile) as f:
        reading_classes = True
        for line in f:
            line = line.rstrip()
            if reading_classes:
                if line == "=":
                    reading_classes = False
                else:
                    read_classes.append(line)
            else:
                final_name = line

    print(f"Classes: {read_classes}")
    print(f"Output: {final_name}")

    # Process headers
    # ex: { 'classname': [ 'iostream', 'string' ] }
    includes: list[str] = []
    # ex: [ 'std::string', 'std::vector' ]
    used: list[str] = []

    # { 'classname': 'class content' }
    content: dict[str, str] = {}

    for read_class in read_classes:
        if os.path.exists(f"{target_dir}/{read_class}.h"):
            print(f"Found header for {read_class}")
            header_vals = processFile(f"{target_dir}/{read_class}.h", debug_mode)
            for using in header_vals['using']:
                if using not in used:
                    used.append(using)
            for include in header_vals['includes']:
                if include not in includes:
                    includes.append(include)
            content[f"{read_class}.h"] = header_vals['content']

        if os.path.exists(f"{target_dir}/{read_class}.cpp"):
            print(f"Found src for {read_class}")
            src_vals = processFile(f"{target_dir}/{read_class}.cpp", debug_mode)
            for using in src_vals['using']:
                if using not in used:
                    used.append(using)
            for include in src_vals['includes']:
                if include not in includes:
                    includes.append(include)
            content[f"{read_class}.cpp"] = src_vals['content']

    with open(final_name, 'w') as f:
        print(f"Writing to file: {final_name}")
        for include in includes:
            f.write(f"#include <{include}>\n")

        using_str = "using "
        for using in used:
            if (debug_mode):
                print(f"Using: {using}")
            using_str += f"{using},"
        using_str = using_str[:-1] + ";\n"
        
        if (debug_mode):
            print(using_str)

        f.write(using_str)
        
        for read_class in read_classes:
            if f"{read_class}.h" in content:
                print(f"Writing contents of {read_class}.h")
                f.write(content[f"{read_class}.h"])
        for read_class in read_classes:
            if f"{read_class}.cpp" in content:
                print(f"Writing contents of {read_class}.cpp")
                f.write(content[f"{read_class}.cpp"])

    print("Done!")