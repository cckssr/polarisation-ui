import matplotlib.pyplot as plt
import pandas as pd

p_polarisation = pd.read_csv("Brewster-Messung-P.csv", delimiter=",")
s_polarisation = pd.read_csv("Brewster-Messung-S.csv", delimiter=",")

plt.plot(
    p_polarisation["sample_angle_deg"],
    p_polarisation["intensity_V"],
    label="p-Polarisation",
)
plt.plot(
    s_polarisation["sample_angle_deg"],
    s_polarisation["intensity_V"],
    label="s-Polarisation",
)
plt.xlabel("Winkel (°)")
plt.ylabel("Intensität (a.u.)")
plt.title("Brewster'scher Winkel Messung")
plt.legend()
plt.grid()
plt.show()
