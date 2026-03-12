from .parsers import PUMLParser
from .shrinking_algorithms import get_algorithm
from typing import TextIO

import os
import json
import tempfile
from enum import StrEnum

class Algorithm(StrEnum):
    evolution = "evol"
    kruskals = "kruskals"
    none = "none"

def process_puml(file: TextIO, algorithm: str, settings: str):
    parser = PUMLParser("app/parsers/parser_config.json")
    source_path = None
    output_path = None

    try:
        algorithm_settings = json.loads(settings)
    except Exception:
        raise TypeError("Invalid settings format")

    print(algorithm)
    print(algorithm_settings)

    try:
        content = file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".puml") as tmp:
            tmp.write(content.encode("utf-8"))
            source_path = tmp.name

        parsed = parser.parse_file(
            source_path
        )
        if not parsed:
            raise TypeError("Unable to parse PUML file")

        if algorithm == Algorithm.evolution:
            alg = get_algorithm("genetic")
            alg.initialize(
                population_size=algorithm_settings.get("population", 50),
                generations=algorithm_settings.get("iterations", 100),
            )
        elif algorithm == Algorithm.kruskals:
            alg = get_algorithm("kruskal")
            # TODO: add settigns
        else:
            raise TypeError("Unknown algorithm")

        reduced = alg.compute(parsed)

        with tempfile.NamedTemporaryFile(
            delete=False, suffix="_reduced.puml"
        ) as tmp_out:
            output_path = tmp_out.name
        parser.reparse_file(source_path, output_path, reduced)
        with open(output_path, "r", encoding="utf-8") as f:
            result = f.read()

        return {"parsed": parsed, "reduced": reduced, "result_puml": result}

    except Exception as e:
        raise RuntimeError(e.__str__())

    finally:
        if source_path and os.path.exists(source_path):
            try:
                os.remove(source_path)
            except:
                pass
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass