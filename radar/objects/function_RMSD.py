from math import cos, sqrt
def angular_coordinates(Beta1, Beta2, L, k_sigma, lambda1, p):
    #p, k_sigma, lambds1 - лежит в input, 
    #Расчет потенциальных СКО определения угловых координат
    delta=k_sigma*lambda1/(L*cos(Beta2-Beta1)*sqrt(p))
    return delta
def RMSD_range(tau, k_sigma, p):
    #tau, k_sigma, p - лежит в input, 
    #Расчет среднеквадратического отклонения измерения дальности
    с=3*10**8
    rmsd=с*k_sigma*tau/sqrt(p)
    return rmsd
def RMSD_speed(tau, lambda1,k_sigma, p):
    #tau, k_sigma, p, lamda1 -лежит в input,
    #Расчет среднеквадратического отклонения измерения скорости для немодулированного сигнала и ФКМ
    speed=k_sigma*lambda1/(sqrt(p)*tau)
    return speed
def RMSD_speed_for_lfm(tau, k_sigma, p, T_0):
    #tau, k_sigma, p, T_0 - лежит в input,
    #Расчет среднеквадратического отклонения измерения скорости для ЛЧМ
    с=3*10**8
    speed=RMSD_range(tau, с, k_sigma, p)*sqrt(2)/T_0
    return speed

