

export function WeatherItem({ id, forecastItem }) {
    const rainPercentage = (forecastItem.rainSum * 100).toFixed(1);
    return (
        <div key={id} className="weather-item flex flex-col items-center justify-center bg-emerald-400 p-5 rounded">
            <img src={rainPercentage > 30 ? 'https://openweathermap.org/img/wn/10d@2x.png' : 'https://openweathermap.org/img/wn/01d@2x.png'} alt="" />
            <div>{forecastItem.date.toLocaleDateString('ru-RU', { weekday: 'long' })}</div>
            <div>{forecastItem.temperatureMin.toFixed(1)}°C - {forecastItem.temperatureMax.toFixed(1)}°C</div>
            <div>Вероятность дождя: {rainPercentage} %</div>
        </div>
    )
}
