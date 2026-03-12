from app import process_puml
import json
import unittest

class TestKruskalAlgorithm(unittest.TestCase):

    def test_kruskal_file1(self):
        file = open(file="puml_files/file1.puml", encoding="UTF-8")

        result = process_puml(
            file=file,
            algorithm="kruskals",
            settings='{}'
        )

        self.assertIsNotNone(result)

        file_sample = open(file="puml_files/file1_kruskal.json", encoding="UTF-8")
        reader = file_sample.read()
        file_sample.close()
        json_sample = json.loads(reader)

        self.assertEqual(result, json_sample)

    def test_kruskal_file2(self):
        file = open(file="puml_files/file2.puml", encoding="UTF-8")

        result = process_puml(
            file=file,
            algorithm="kruskals",
            settings='{}'
        )

        self.assertIsNotNone(result)

        file_sample = open(file="puml_files/file2_kruskal.json", encoding="UTF-8")
        reader = file_sample.read()
        file_sample.close()
        json_sample = json.loads(reader)

        self.assertEqual(result, json_sample)

    def test_kruskal_file3(self):
        file = open(file="puml_files/file3.puml", encoding="UTF-8")

        result = process_puml(
            file=file,
            algorithm="kruskals",
            settings='{}'
        )

        self.assertIsNotNone(result)

        file_sample = open(file="puml_files/file3_kruskal.json", encoding="UTF-8")
        reader = file_sample.read()
        file_sample.close()
        json_sample = json.loads(reader)

        self.assertEqual(result, json_sample)

class TestGenericAlgorithm(unittest.TestCase):

    def test_evolution_file1(self):
        file = open(file="puml_files/file1.puml", encoding="UTF-8")

        result = process_puml(
            file=file,
            algorithm="evol",
            settings='{"iterations": 5}'
        )

        self.assertIsNotNone(result)

    def test_evolution_file2(self):
        file = open(file="puml_files/file2.puml", encoding="UTF-8")

        result = process_puml(
            file=file,
            algorithm="evol",
            settings='{"iterations": 5}'
        )

        self.assertIsNotNone(result)

    def test_evolution_file3(self):
        file = open(file="puml_files/file3.puml", encoding="UTF-8")

        result = process_puml(
            file=file,
            algorithm="evol",
            settings='{"iterations": 5}'
        )

        self.assertIsNotNone(result)