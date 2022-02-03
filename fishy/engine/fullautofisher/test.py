import logging

from fishy.engine.fullautofisher.engine import FullAuto


class Test:
    def __init__(self, engine: FullAuto):
        self.engine = engine
        self.target = None

    # noinspection PyProtectedMember
    def print_coords(self):
        logging.info(self.engine.get_coords())

    def set_target(self):
        self.target = self.engine.get_coords()
        logging.info(f"target_coods are {self.target}")

    def move_to_target(self):
        if not self.target:
            logging.info("please set a target first")
        self.engine.move_to(self.target)

    def rotate_to_target(self):
        if not self.target:
            logging.info("please set a target first")
        self.engine.rotate_to(self.target[2])

    def look_for_hole(self):
        logging.info("looking for a hole")

        if self.engine.look_for_hole():
            logging.info("found a hole")
        else:
            logging.info("no hole found")
