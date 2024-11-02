import { useEffect, useState } from 'react';
import HistoryIcon from '../assets/recent-icon.svg?react';
import { Layout } from '../components/layout'
import { UiModal, UiButton, WeatherItem, Autocomplete, ListItem } from '../components'
import axios from 'axios'
import { serverURL } from '../constants';


export function DailyForecast() {
  const [weatherData, setWeatherData] = useState(null);
  const [error, setError] = useState(null);
  const [lastViewedCity, setLastViewedCity] = useState(null);
  const [searchHistory, setSearchHistory] = useState(null);

  const getLastViewedCity = async () => {
    await axios.get(serverURL + '/forecast/last-viewed-city/', {withCredentials: true})
    .then((resp) => {
      console.log(resp.data); 
      setLastViewedCity(resp.data.last_viewed_city);
      setError(null);
    })
    .catch((err) => {
      if (err.response.status === 404 && "last_viewed_city" in err.response.data) {
        setLastViewedCity(null);
        return
      }
      console.error(err);
      setError('Something went wrong, try again later');
      setWeatherData(null);
    });
  }

  const getForecastByCity = async (cityName) => {
    await axios.get(serverURL + '/forecast/daily/', { params: { location: cityName }, withCredentials: true })
    .then((resp) => {
      setWeatherData(resp.data)
      setError(null);
    })
    .catch((err) => {
      console.error(err);
      setError('Произошла ошибка при получении данных о погоде, пожалуйста попробуйте позже');
      setWeatherData(null);
    });
  }

  const getForecastByCoords = async (coordinates) => {
    await axios.get(serverURL + '/forecast/', { params: { lat: coordinates.latitude, lon: coordinates.longitude }, withCredentials: true })
    .then((resp) => {
      console.log(resp.data); 
      setWeatherData(resp.data)
      setError(null);
    })
    .catch((err) => {
      console.error(err);
      setError('Произошла ошибка при получении данных о погоде, пожалуйста попробуйте позже');
      setWeatherData(null);
    });
  }

  const getSearchHistory = async () => {
    await axios.get(serverURL + '/forecast/search-history/', {withCredentials: true})
    .then((resp) => {
      setSearchHistory(resp.data);
    })
    .catch((err) => {
      console.error(err);
      setSearchHistory(null);
    });
  }

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    const data = new FormData(e.target)
    const cityName = data.get('city_name')
    if (cityName && cityName != weatherData?.location) {
      await getForecastByCity(cityName)
    }
  }

  const formatWeatherData = (data) => {
    const formattedData = {location: data.city, forecast: []};
    for (const [date, forecast] of Object.entries(data.forecast)) {
      formattedData.forecast.push({
        date: new Date(date),
        ...forecast
      });
    }
    console.log(formattedData);
    

    return formattedData;
  };

  const getCitiesCompletions = async (query) => {
    const url = new URL("https://api.thecompaniesapi.com/v1/locations/cities");
    url.search = new URLSearchParams({ token: 'fUrFHu1E', search: query, size: 5 }).toString();

    return fetch(url)  // Возвращаем промис
    .then((resp) => resp.json())
    .then((data) => {
        const cities = [];
        data.cities.forEach(city => {
            cities.push({cityName: city.name, countryName: city.country.name});
        });
        return cities;  // Возвращаем массив после заполнения
    });
};


  const showCitiesCompletions = (complition, inpValue) => {
    return (
        complition.cityName && complition.countryName ? (
          <div>
            <p className='text-lg'>
              <strong>{complition.cityName.substr(0, inpValue.length)}</strong>
              { complition.cityName.substr(inpValue.length) }
            </p>
            <p>{complition.countryName}</p>
          </div>
        ) : "No matches found"
    )
  }

  const form = (
      <form onSubmit={handleFormSubmit} className='flex flex-col items-center' autoComplete="off">
        <div>
          <Autocomplete
           getMatchesCallback={getCitiesCompletions}
           showMatchesCallback={showCitiesCompletions}
           suggestionResolver={(suggestion) => suggestion.cityName}
           className={"mb-4"}
           inputProps={{ name: 'city_name', placeholder: 'Город', required: true, onFocus: (e) => {
            const ul = e.target.closest('form').querySelector('ul#search-history')
            ul.classList.remove('hidden')
            getSearchHistory()
           }}}
          />
          <ul className='bg-white' id="search-history">
            {searchHistory?.results && searchHistory.results.map((obj, index) => {
              return (
                <ListItem key={index} onClick={(e) => {
                  const ul = e.target.closest('ul#search-history')
                  ul.classList.remove('hidden')
                  if (obj.city_name !== weatherData?.location) {
                    ul.classList.add('hidden')
                    const input = ul.parentNode.querySelector('input[name="city_name"]')
                    input.value = obj.city_name
                    getForecastByCity(obj.city_name)
                    console.log("setted input value and got forecast");
                  }
                }}>
                  {obj.city_name} <span className='ml-2'><HistoryIcon width="16" height="16"/></span>
                </ListItem>
              )
            })}
          </ul>
        </div>
        <UiButton variant="primary" size="lg" disabled={Boolean(error)}>
          Посмотреть погоду
        </UiButton>
      </form>

  )
  
  const modal = (
    <UiModal
      isOpen={Boolean(lastViewedCity)}
      onClose={() => setLastViewedCity(null)}
    >
      <UiModal.Header>Хотите узнать погоду в недавно просмотренном городе {lastViewedCity}?</UiModal.Header>
      <UiModal.Footer>
        <UiButton variant='outline' onClick={() => setLastViewedCity(null)}>Нет</UiButton>
        <UiButton variant="primary" onClick={
          async () => {
            setLastViewedCity(null)
            await getForecastByCity(lastViewedCity)
          }}
        >
          Да
        </UiButton>
        <UiButton variant='primary' onClick={() => {
          setLastViewedCity(null)
          const successCallback = (position) => getForecastByCoords(position.coords)
          const errorCallback = (err) => {
            setError("Can't get your location")
            console.error(err)
          }
          navigator.geolocation.getCurrentPosition(successCallback, errorCallback)
        }}>
          Посмотреть погоду по моей текущей геолокации
        </UiButton>
      </UiModal.Footer>
    </UiModal>
  )

  useEffect(() => {
    (async () => await getLastViewedCity())()
  }, [])

  return (
    <>
      <Layout form={form} modal={modal}>
      {error && <p className="text-red-500 text-2xl mt-3">{error}</p>}
      {weatherData && (
        <div className='my-5'>
          <h3 className="text-2xl mb-3">Прогноз погоды в городе {weatherData.location} на ближайшее время.</h3>
          <div className="weather-container flex gap-3 flex-wrap justify-center">
            {formatWeatherData(weatherData).forecast.map((item, index) => (
              <WeatherItem key={index} forecast={item} location={weatherData.location}/>
            ))}
          </div>
        </div>
      )}
      </Layout>
    </>
  )
}
