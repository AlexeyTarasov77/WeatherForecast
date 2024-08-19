import { useState } from 'react';
import { Layout } from './components/layout'
import { UiFieldInput, UiModal, UiButton, WeatherItem } from './components'
import axios from 'axios'


export default function App() {
  const [weatherData, setWeatherData] = useState(null);
  const [error, setError] = useState(null);

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    const data = new FormData(e.target)
    const cityName = data.get('city_name')
    await axios.get('http://127.0.0.1:8000/forecast/', { params: { city_name: cityName } })
    .then((resp) => {
      console.log(resp.data); 
      resp.data.city = cityName
      setWeatherData(resp.data)
      setError(null);
    })
    .catch((err) => {
      console.error(err);
      setError('Error fetching weather data, try again later');
      setWeatherData(null);
    });
  }

  const formatWeatherData = (data) => {
    const formattedData = [];
    const dates = data.daily.date;
    const temperatureMins = data.daily.temperature_2m_min;
    const temperatureMaxs = data.daily.temperature_2m_max;
    const rainSums = data.daily.rain_sum;

    for (let i = 0; i < Object.keys(dates).length; i++) {
      console.log(dates[i]);
      
      formattedData.push({
        date: new Date(dates[i]),
        temperatureMin: temperatureMins[i],
        temperatureMax: temperatureMaxs[i],
        rainSum: rainSums[i],
      });
    }

    return formattedData;
  };

  const form = (
    <form onSubmit={handleFormSubmit}>
      <UiFieldInput
        className={"mb-4"}
        placeholder="Ваш город"
        id="city"
        name="city_name"
        required
      />
      <UiButton variant="primary" size="lg" disabled={Boolean(error)}>
        Отправить
      </UiButton>
    </form>
  )

  return (
    <>
      <Layout form={form}>
      {error && <p className="text-red-500 text-2xl mt-3">{error}</p>}
      {weatherData && (
        <div className='my-5'>
          <h3 className="text-2xl mb-3">Прогноз погоды в городе {weatherData.city} на ближайшее время.</h3>
          <div className="weather-container flex gap-3 flex-wrap justify-center">
            {formatWeatherData(weatherData).map((item, index) => (
              <WeatherItem key={index} forecastItem={item}/>
            ))}
          </div>
        </div>
      )}
      </Layout>
    </>
  )
}
