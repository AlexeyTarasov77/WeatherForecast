

export function WeatherItem({ forecast, location }) {
    const pp = forecast.precipitation_probability
    const tempMin = forecast.temp_min
    const tempMax = forecast.temp_max
    const weatherItemOnClick = () => window.location.href = `/forecast/hourly/${forecast.date.toISOString()}?location=${location}`
    const computePrecipitation = (probability) => {
        if (probability % 10 === 5) {
            return probability
        }
        return Math.round(probability / 10) * 10
    }
    let dayOfWeek = forecast.date.toLocaleDateString('ru-RU', { weekday: 'long' })
    dayOfWeek = dayOfWeek.charAt(0).toUpperCase() + dayOfWeek.slice(1)
    return (
        <div className="weather-item flex flex-col items-center justify-center bg-emerald-400 p-5 rounded hover:cursor-pointer" onClick={weatherItemOnClick}>
            <img src={pp.value > 20 ? 'https://openweathermap.org/img/wn/10d@2x.png' : 'https://openweathermap.org/img/wn/01d@2x.png'} alt="" />
            <div className="text-2xl font-mono font-bold">{dayOfWeek}</div>
            <div>
                <p><span className="text-lime-100">{tempMin.value.toFixed(0)} {tempMin.unit}</span> - <span className="text-blue-600">{tempMax.value.toFixed(0)} {tempMax.unit}</span></p>
            </div>
            <div>
                Вероятность осадков: &nbsp;
                <span className="text-lg font-bold">{computePrecipitation(pp.value)} {pp.unit}</span>
            </div>
        </div>
    )
}
