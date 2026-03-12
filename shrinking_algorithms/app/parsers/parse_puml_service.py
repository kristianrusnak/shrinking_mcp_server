import json
import re

class PUMLParser:
    def __init__(self, config_path="parser_config.json"):
        self.relations = {}
        self.class_names = set()
        self.parse_config(config_path)

        if not self.relations:
            print("No relations loaded, using default settings.")
            return

    def parse_config(self, config_path):
        if config_path is None:
            print("No config path provided, loading default config.")
            return {}

        try:
            with open(config_path, "r") as file:
                config = json.load(file)
                self.relations = config.get("relations", {})
                self.class_names = set(config.get("class_names", []))
                return config

        except Exception as e:
            print(f"Error reading config file: {e}")
            return {}

    def check_correct_puml(self, file) -> bool:
        start_found = False
        end_found = False

        for line in file:
            line = line.strip()
            if line == "@startuml":
                start_found = True
            elif line == "@enduml":
                end_found = True

        return start_found and end_found

    def remove_comments(self, file):
        file.seek(0)
        content = file.read()

        content = re.sub(r"/\'.*?\'\/", "", content, flags=re.DOTALL)

        return content.split("\n")

    def parse_file(self, filepath) -> dict | list:

        with open(filepath, "r") as file:
            if not self.check_correct_puml(file):
                print("File is not a correct PUML file.")
                return []

            lines = self.remove_comments(file)

            classes = {}
            classesCount = 0
            edges = []
            current_class = None
            in_class_body = False

            for i, line in enumerate(lines):
                line = line.strip()
                is_class_declaration = False

                for keyword in self.class_names:
                    if line.startswith(keyword):
                        class_name = self.extract_class_name(keyword, line)
                        if class_name:
                            current_class = class_name
                            classes[class_name] = {
                                "id": classesCount,
                                "attributes": [],
                                "methods": []
                            }
                            classesCount += 1
                            in_class_body = line.endswith("{")
                            is_class_declaration = True
                        break

                if in_class_body and line == "}":
                    in_class_body = False
                    current_class = None
                    continue

                if in_class_body and current_class and not is_class_declaration:
                    member = self.parse_class_member(line)
                    if member:
                        if member["type"] == "attribute":
                            classes[current_class]["attributes"].append({
                                "name": member["name"],
                                "visibility": member["visibility"],
                                "datatype": member.get("datatype", "")
                            })
                        elif member["type"] == "method":
                            classes[current_class]["methods"].append({
                                "name": member["name"],
                                "visibility": member["visibility"],
                                "signature": member["signature"]
                            })

                for relation_key, relation_value in self.relations.items():
                    line_without_brackets = re.sub(r'\[.*?\]', '', line.strip())
                    if relation_key in line_without_brackets:
                        parts = line_without_brackets.split(relation_key)
                        edge = self.extract_edge_info(parts)
                        
                        source = edge.get("source")
                        target = edge.get("target")
                        if source in classes and target in classes:
                            edges.append(edge | {"relation": relation_value})
                        break

            return {"classes": classes, "edges": edges}

    def extract_class_name(self, keyword, line):
        name = line.replace(keyword + " ", "").split(" ")[0].strip()
        if name:
            return name
        return ""

    def extract_edge_info(self, parts) -> dict:
        if len(parts) == 2:
            source = parts[0]
            target = parts[1]
            
            if ':' in target:
                target = target.split(':')[0].strip()

            if '"' in source:
                source = source.split('"')[0].strip()

            if '"' in target:
                target = target.split('"')[-1].strip()

            return {"source": source, "target": target}
        return {}

    def reparse_file(self, source_path, output_path, new_data):

        if source_path is None or output_path is None:
            print("Source or output path is None.")
            return

        if not new_data:
            print("No new data provided for reparsing.")
            return

        lines = []
        current_class = None
        in_class_body = False
        skip_class = False

        with open(source_path, "r") as file:
            for line in file:
                appendLine = True
                stripped_line = line.strip()
                is_class_declaration = False

                for keyword in self.class_names:
                    if stripped_line.startswith(keyword):
                        class_name = self.extract_class_name(keyword, stripped_line)
                        if class_name:
                            current_class = class_name
                            is_class_declaration = True
                            if class_name not in new_data.get("classes", {}):
                                skip_class = True
                                appendLine = False
                            else:
                                skip_class = False
                                in_class_body = stripped_line.endswith("{")
                        break

                if in_class_body and stripped_line == "}":
                    in_class_body = False
                    if skip_class:
                        appendLine = False
                    current_class = None
                    skip_class = False

                elif skip_class:
                    appendLine = False

                elif in_class_body and current_class and current_class in new_data.get("classes", {}) and not is_class_declaration:
                    member = self.parse_class_member(stripped_line)
                    if member:
                        class_data = new_data["classes"][current_class]
                        
                        if member["type"] == "attribute":
                            attr_exists = any(
                                attr["name"] == member["name"] and 
                                attr["visibility"] == member["visibility"]
                                for attr in class_data.get("attributes", [])
                            )
                            if not attr_exists:
                                appendLine = False
                        
                        elif member["type"] == "method":
                            method_exists = any(
                                method["signature"] == member["signature"] and
                                method["visibility"] == member["visibility"]
                                for method in class_data.get("methods", [])
                            )
                            if not method_exists:
                                appendLine = False

                if not is_class_declaration:
                    for relation_key, relation_value in self.relations.items():
                        line_without_brackets = re.sub(r'\[.*?\]', '', stripped_line)
                        if relation_key in line_without_brackets:
                            lineWithoutComments = re.sub(r"/\'.*?'\/", "", line_without_brackets, flags=re.DOTALL).strip()
                            parts = lineWithoutComments.split(relation_key)
                            edge = self.extract_edge_info(parts)
                            
                            source = edge.get("source")
                            target = edge.get("target")
                            
                            # Check if this edge exists in new_data
                            edge_exists = False
                            for new_edge in new_data.get("edges", []):
                                if (new_edge.get("source") == source and 
                                    new_edge.get("target") == target and 
                                    new_edge.get("relation") == relation_value):
                                    edge_exists = True
                                    break
                            
                            if not edge_exists:
                                appendLine = False
                            elif source not in new_data.get("classes", {}) or target not in new_data.get("classes", {}):
                                appendLine = False
                            break

                if appendLine:
                    lines.append(line)

        with open(output_path, "w") as file:
            file.writelines(lines)

    def parse_class_member(self, line):
        """Parse a class member (attribute or method) with visibility modifier."""
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("'"):
            return None

        visibility_map = {"+": "public", "-": "private", "#": "protected", "~": "package"}
        visibility = "public"
        
        if line and line[0] in visibility_map:
            visibility = visibility_map[line[0]]
            line = line[1:].strip()

        if "(" in line and ")" in line:
            method_match = re.match(r'([a-zA-Z_]\w*)\s*\((.*?)\)', line)
            if method_match:
                method_name = method_match.group(1)
                params = method_match.group(2).strip()
                signature = f"{method_name}({params})"
                return {
                    "type": "method",
                    "name": method_name,
                    "visibility": visibility,
                    "signature": signature
                }
        
        else:
            attr_match = re.match(r'([a-zA-Z_]\w*)\s*(?::\s*(.+))?', line)
            if attr_match:
                attr_name = attr_match.group(1)
                datatype = attr_match.group(2).strip() if attr_match.group(2) else ""
                return {
                    "type": "attribute",
                    "name": attr_name,
                    "visibility": visibility,
                    "datatype": datatype
                }

        return None
