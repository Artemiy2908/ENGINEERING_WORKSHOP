from copy import deepcopy
from datetime import datetime
from typing import TypeVar
import sqlite3

import logger
from function_RMSD import angular_coordinates, RMSD_range, RMSD_speed, RMSD_speed_for_lfm
import objects.maneuvers as maneuvers
from coordinates.coordinates import Coordinates3D, CoordinatesGCS
from coordinates.vectors import Vector3D, VectorGCS, VectorLECS

V = TypeVar("V", Vector3D, VectorGCS, VectorLECS)
C = TypeVar("C", Coordinates3D, CoordinatesGCS)
M = TypeVar("M", maneuvers.ChangeHeight,
            maneuvers.ChangeSpeed, maneuvers.CenterFold)


class Aircraft:

    def __init__(self, name: str, position: C, speed: V, acceleration: V,
                 radius: float = 1):
        self.name: str = name
        self.position: C = deepcopy(position)
        self.speed: V = deepcopy(speed)
        self.acceleration: V = deepcopy(acceleration)

        self.effective_scattering_area = 10  # meters^2
        self.centerfold_radius: float = 10
        self.reflection_radius: float = radius

        self.__trajectory: list[C] = [deepcopy(position)]

        self.__current_maneuvers: list[M] = []
        self.__logger = logger.get_aircraft_logger(__name__)
        self.__filename = f"trajectories/'{name}'_{datetime.now()}.txt"
        open(self.__filename, "w").close()

    def __write_position(self):
        connection = sqlite3.connect('C:/Users/PC/Desktop/python_code/database2.db')
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM Output_parameters')
        total_users = cursor.fetchone()[0]
        coord=cursor.execute('SELECT sigma_x FROM Output_parameters where = ?', (total_users))
        c = self.position
        if coord:
            cursor.execute('UPDATE Output_parameters SET sigma_x=?, sigma_y=?, sigma_h=? where Number_test = ?', (c.x, c.y, c.z, total_users))
        else:
            total_users+=1
            cursor.execute('INSERT INTO Output_parameters (Number_test, sigma_x, sigma_y, sigma_h) VALUES (?, ?, ?)', (total_users, c.x, c.y, c.z))
        tau=cursor.execute('SELECT duration_impulse FROM Intput_parameters where = ?', (total_users))
        lambda1=cursor.execute('SELECT Wavelength FROM Intput_parameters where = ?', (total_users))
        k_sigma=cursor.execute('SELECT Proportionality_coefficient_RMSD FROM Intput_parameters where = ?', (total_users))
        p=cursor.execute('SELECT Signal_to_noise_ratio FROM Intput_parameters where = ?', (total_users))
        type_signal=cursor.execute('SELECT Type_of_signal_modul FROM Intput_parameters where = ?', (total_users))
        T_0=cursor.execute('SELECT Frequency_of_LFM_radiation FROM Intput_parameters where = ?', (total_users))
        angular_coordinates() #НЕ ХВАТАТЕ ДАННЫХ
        rmsd_range=RMSD_range(tau, k_sigma, p)
        if type_signal==1:
            rmsd_speed=RMSD_speed_for_lfm(tau, k_sigma, p, T_0)
            cursor.execute('UPDATE Output_parameters SET delta_D=?, delra_V where Number_test = ?', (rmsd_range, rmsd_speed, total_users))
        else:
            rmsd_speed=RMSD_speed(tau, lambda1, k_sigma, p)
            cursor.execute('UPDATE Output_parameters SET delta_D=?, delra_V where Number_test = ?', (rmsd_range, rmsd_speed, total_users))

        connection.commit()
        connection.close() 
        with open(self.__filename, "a") as file:
            c = self.position
            file.write(f"{c.x};{c.y};{c.z}\n")

    def make_maneuver(self, maneuver: M):
        self.__current_maneuvers.append(maneuver)
        self.__current_maneuvers[-1].prepare()

    def update(self, dt: float = 1.0) -> None:
        for_deletion = []

        # TODO: make better this code
        for i in range(len(self.__current_maneuvers)):
            if self.__current_maneuvers[i].is_finished:
                self.__logger.info(f"Finished maneuver "
                                   f"{self.__current_maneuvers[i].__class__}")
                for_deletion.append(i)
            else:
                self.__current_maneuvers[i].do()

        for index in for_deletion:
            self.__current_maneuvers.pop(index)
        # this code
        self.position += self.speed * dt + (self.acceleration * dt ** 2) / 2
        self.speed += self.acceleration * dt
        self.__logger.info(f"{self}")

        self.__trajectory.append(deepcopy(self.position))
        self.__write_position()

    def get_trajectory(self) -> list[C]:
        return deepcopy(self.__trajectory)

    def __str__(self):
        return (f"Aircraft(name: {self.name}, "
                f"position: {str(self.position)}, speed: {str(self.speed)}, "
                f"acceleration: {str(self.acceleration)})")

    def __repr__(self):
        return (f"AerialObject({self.name}, {self.position}, {self.speed}, "
                f"{self.acceleration})")
