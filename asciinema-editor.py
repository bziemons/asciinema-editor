#!/usr/bin/env python

import json
import sys
from typing import Tuple, List


class Recording(object):
    def __init__(self, desc, lines):
        self.desc = desc
        self.lines = lines

    @classmethod
    def from_file(cls, filename):
        with open(filename, "r", encoding="utf-8") as f:
            desc = json.loads(f.readline())
            lines = []
            for line in f.readlines():
                lines.append(json.loads(line))
            return cls(desc, lines)

    def write(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            desc_line = json.dumps(self.desc) + "\n"
            f.write(desc_line)
            for line in self.lines:
                line = json.dumps(line) + "\n"
                f.write(line)

    def recalculate(self, operations: List[Tuple]):
        # sort by end line
        operations.sort(key=lambda x: x[1])
        for op in operations:
            if op[2] == "set":
                start = op[0] - 2
                end = op[1] - 2
                difference = op[3] - self.lines[end][0]
                for i in range(start, end + 1):
                    self.lines[i][0] = op[3]
                self.apply_offset(end + 1, difference)
            elif op[2] == "offset":
                start = op[0] - 2
                self.apply_offset(start, op[3])
            elif op[2] == "linear":
                start = op[0] - 2
                end = op[1] - 2
                start_sec = self.lines[start][0]
                old_ending_sec = self.lines[end][0]
                for i in range(start + 1, end + 1):
                    self.lines[i][0] = start_sec + (op[3] * (i - start))
                new_ending_sec = self.lines[end][0]
                self.apply_offset(end + 1, new_ending_sec - old_ending_sec)
            elif op[2] == "timelapse":
                start = op[0] - 2
                end = op[1] - 2
                start_sec = self.lines[start][0]
                old_ending_sec = self.lines[end][0]
                new_length_sec = op[3]
                step_sec = new_length_sec / (old_ending_sec - start_sec)
                for i in range(start + 1, end + 1):
                    self.lines[i][0] = start_sec + (
                        (self.lines[i][0] - start_sec) * step_sec
                    )
                new_ending_sec = self.lines[end][0]
                self.apply_offset(end + 1, new_ending_sec - old_ending_sec)

    def apply_offset(self, start, offset):
        for i in range(start, len(self.lines)):
            self.lines[i][0] += offset


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} [input file] [output file]", file=sys.stderr)
        sys.exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    r = Recording.from_file(input_filename)
    r.recalculate(
        [
            (7, 7, "set", 1.5),
            (7, 22, "linear", 0.05),
            (31, 52, "linear", 0.05),
            (55, 55, "offset", -2),
            (60, 60, "offset", -1),
            (60, 79, "linear", 0.05),
            (85, 85, "offset", -5),
            (85, 120, "linear", 0.05),
            (122, 145, "timelapse", 1),
            (146, 173, "linear", 0.05),
            (174, 657, "timelapse", 5),
        ]
    )
    r.write(output_filename)


if __name__ == "__main__":
    main()
