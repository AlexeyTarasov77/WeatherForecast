import { UiButton } from "./button"


export function WeatherDetail({ data }) {
    const tempMin = data.forecast.temp_min
    const tempMax = data.forecast.temp_max
    const hourlyForecast = data.forecast.hourly
    const date = new Date(data.date)
    const currTemp = hourlyForecast[Object.keys(hourlyForecast).find(key => new Date(key).getHours() === new Date().getHours())].temp
    const displayHours = (date) => {
        let dateHours = new Date(date).getHours()
        if (new Date().getHours() === dateHours) {
            return 'Now'
        } else if(new Date(date).getHours() < 10) {
            return `0${dateHours}`
        }
        return new Date(date).getHours()
    }
    
    return (
        <>
            <div className="my-5 mx-3"><UiButton onClick={() => window.history.back()}>Back to forecast</UiButton></div>
            <div className="flex flex-col items-center justify-center bg-emerald-500 p-5">
                <div className="text-2xl font-bold">{data.location}</div>
                <h5>{date.getDate() === new Date().getDate() ? 'Сегодня' : date.toLocaleDateString('ru-RU', { weekday: 'long' })}</h5>
                <div className="text-4xl">{currTemp.value.toFixed(0)} {currTemp.unit}</div>
                <div className="flex gap-2">
                    <p><strong>Min:</strong>{tempMin.value} {tempMin.unit}</p>
                    <p><strong>Max:</strong>{tempMax.value} {tempMax.unit}</p>
                </div>
                <div className="mt-10 flex gap-2">
                    {Object.keys(hourlyForecast).map((date, index) => (
                        <div key={index} className="flex flex-col items-center justify-between">
                            <div><strong>{displayHours(date)}</strong></div>
                            <div>{hourlyForecast[date].temp.value.toFixed(0)} {hourlyForecast[date].temp.unit}</div>
                        </div>
                    ))}
                </div>
            </div>
        </>
    )
}