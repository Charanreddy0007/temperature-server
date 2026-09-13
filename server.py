from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import os

app = FastAPI()

API_KEY = os.environ.get("API_KEY")


@app.post("/generate-graph")
async def generate_graph(request: Request):

    # ==========================
    # AUTHENTICATION
    # ==========================

    authorization = request.headers.get("Authorization")
    
    if authorization != "Bearer " + API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    # ==========================================
    # RECEIVE CSV FROM WEMOS
    # ==========================================

    csv_data = await request.body()

    print("CSV received:", len(csv_data), "bytes")

    # Read CSV directly from request
    df = pd.read_csv(io.BytesIO(csv_data))

    # Remove accidental spaces from headers
    df.columns = df.columns.str.strip()

    print("Headers:", list(df.columns))
    print("Rows:", len(df))


    # ==========================================
    # CONVERT TIME
    # ==========================================

    plot_time = pd.to_datetime(
        df["time"],
        format="%H:%M:%S"
    )


    # ==========================================
    # GET TEMPERATURE DATA
    # ==========================================

    sensor_temperature = df[
        "sensor_temperature"
    ].values

    weather_temperature = df[
        "weather_temperature"
    ].values


    # ==========================================
    # PLOT
    # ==========================================

    fig, ax = plt.subplots(figsize=(16, 7))


    # ==========================================
    # SENSOR TEMPERATURE
    # ==========================================

    ax.plot(
        plot_time,
        sensor_temperature,
        color="royalblue",
        linewidth=2.5,
        label="DS18B20 Temperature (°C)"
    )


    # ==========================================
    # WEATHER TEMPERATURE
    # ==========================================

    ax.plot(
        plot_time,
        weather_temperature,
        color="crimson",
        linewidth=2.5,
        label="Weather Temperature (°C)"
    )


    # ==========================================
    # Y AXIS - ADD PADDING
    # ==========================================

    all_temp = list(sensor_temperature) + list(
        weather_temperature
    )

    minimum = min(all_temp)
    maximum = max(all_temp)

    padding = max(
        (maximum - minimum) * 0.4,
        0.5
    )

    ax.set_ylim(
        minimum - padding,
        maximum + padding
    )


    # ==========================================
    # LABELS
    # ==========================================

    ax.set_xlabel(
        "Time",
        fontsize=13
    )

    ax.set_ylabel(
        "Temperature (°C)",
        fontsize=13
    )


    # ==========================================
    # TIME AXIS
    # ==========================================

    ax.xaxis.set_major_locator(
        mdates.HourLocator(interval=1)
    )

    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%H:%M")
    )

    ax.xaxis.set_minor_locator(
        mdates.MinuteLocator(interval=15)
    )


    # ==========================================
    # GRID
    # ==========================================

    ax.grid(
        True,
        which="major",
        alpha=0.3
    )

    ax.grid(
        True,
        which="minor",
        alpha=0.12
    )


    # ==========================================
    # TITLE
    # ==========================================

    ax.set_title(
        "Sensor vs Weather Temperature",
        fontsize=18,
        fontweight="bold",
        pad=15
    )


    # ==========================================
    # LEGEND
    # ==========================================

    ax.legend(
        loc="upper left",
        fontsize=11,
        frameon=True
    )


    # ==========================================
    # ROTATE TIME
    # ==========================================

    plt.xticks(rotation=45)

    plt.tight_layout()


    # ==========================================
    # CREATE IMAGE IN MEMORY
    # ==========================================

    image = io.BytesIO()

    plt.savefig(
        image,
        format="png",
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    image.seek(0)

    # ==========================================
    # RETURN GRAPH TO WEMOS
    # ==========================================

    return Response(
        content=image.read(),
        media_type="image/png"
    )