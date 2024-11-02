import { useLoaderData } from "react-router-dom";
import { serverURL } from "../constants";
import { WeatherDetail } from "../components/weather-detail";

async function getHourlyForecast(date) {
    const url = new URL(window.location.href);
    const locationParam = new URLSearchParams(url.search).get('location')
    if (!locationParam) {
        throw new Error("Location must be provided to get hourly forecast");
    }
    return fetch(`${serverURL}/forecast/hourly/${date}?location=${locationParam}`)
    .then((resp) => resp.json())
    .then((data) => {
        console.log("Data from resp", data);
        const processedHourlyData = {}
        Object.entries(data.forecast.hourly).forEach(([key, value]) => {
            console.log('setting value', key, value);
            processedHourlyData[new Date(key).toISOString()] = value
        })
        data.forecast.hourly = processedHourlyData
        return data;
    })
}

export async function loader({ params }) {
    return await getHourlyForecast(params.date);
}

export function HourlyForecast() {
    const data = useLoaderData();
    console.log("DATA", data);
    
    return (
        <div>
            <WeatherDetail data={data} />
        </div>
    )
}