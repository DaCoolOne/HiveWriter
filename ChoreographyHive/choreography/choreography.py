from typing import Set, List

from rlbot.utils.structures.game_data_struct import GameTickPacket

from choreography.drone import Drone

from choreography.constants import BPM, Div_60

BPS = BPM * Div_60

class Choreography:

    def __init__(self):
        self.sequence = []
        self.sequence_index = 0
        self.finished = False
        self.start_time = None
        self.stage_time = 0

    def step(self, packet: GameTickPacket, drones: List[Drone]):
        if not self.start_time:
            self.start_time = packet.game_info.seconds_elapsed
            self.sequence[self.sequence_index].start_beat = 0

        step = self.sequence[self.sequence_index]
        result = step.perform(packet, drones, (packet.game_info.seconds_elapsed - self.start_time) * BPS)
        if result.finished:
            self.sequence_index += 1
            self.stage_time += result.execute_time
            if self.sequence_index < len(self.sequence):
                new_step = self.sequence[self.sequence_index]
                new_step.start_beat = self.stage_time
            else:
                self.finished = True

    def generate_sequence(self):
        raise NotImplementedError
