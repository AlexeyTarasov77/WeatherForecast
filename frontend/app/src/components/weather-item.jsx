

export function WeatherItem({ forecastItem }) {
    const pp = forecastItem.precipitation_probability_max
    const tempMin = forecastItem.temperature_2m_min
    const tempMax = forecastItem.temperature_2m_max
    const appTempMin = forecastItem.apparent_temperature_min
    const appTempMax = forecastItem.apparent_temperature_max
    return (
        <div className="weather-item flex flex-col items-center justify-center bg-emerald-400 p-5 rounded">
            <img src={pp.val > 20 ? 'https://openweathermap.org/img/wn/10d@2x.png' : 'https://openweathermap.org/img/wn/01d@2x.png'} alt="" />
            <div>{forecastItem.date.toLocaleDateString('ru-RU', { weekday: 'long' })}</div>
            <div>
                <p>
                    <span>От: </span>
                    {tempMin.val.toFixed(1)} {tempMin.unit},
                     Ощущается как {appTempMin.val.toFixed(1)} {appTempMin.unit}
                </p> 
                <br />
                <p>
                    <span>До: </span>
                    {tempMax.val.toFixed(1)} {tempMax.unit},
                     Ощущается как {appTempMax.val.toFixed(1)} {appTempMax.unit}
                </p>
            </div>
            <div>
                <span>Вероятность осадков: </span>
                {
                    (
                        pp.val % 10 === 5 ?
                        pp.val :
                        Math.round(pp.val / 10) * 10
                    )
                } 
                {pp.unit}
            </div>
        </div>
    )
}
