export class API {
  #tokenPath
  #token
  constructor(baseUrl = "", tokenPath = "username", credentials = "same-origin") {
    this.#tokenPath = tokenPath;
    this.baseUrl = baseUrl;
    this.credentials = credentials;
  }
  set Token(token) {
    this.#token = token
  }
  async request(method, endpoint, { body, headers = {} } = {}) {

    try {
      const url = `${this.baseUrl.replace(/\/$/, "")}/${String(endpoint).replace(/^\//, "")}`;
      const token = typeof window === 'undefined'
        ? null
        : (!this.#tokenPath)
          ? null
          : localStorage.getItem(this.#tokenPath)
      const defaultHeaders = {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `${this.#token ?? token}` }),
      };
      const mergedHeaders = {
        ...defaultHeaders,
        ...headers,
      };
      if (body instanceof FormData) {
        delete mergedHeaders['Content-Type'];
      }
      const config = {
        method,
        headers: mergedHeaders,
        credentials: this.credentials
      };

      if (body && method !== 'GET') {
        config.body = body instanceof FormData ? body : JSON.stringify(body);
      }
      const response = await fetch(url, config);

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
          console.log("error data:", errorData);
        } catch {
          console.log(response)
          errorData = { message: response.statusText };
        }

        document.dispatchEvent(
          new CustomEvent('error-received', {
            detail: {
              status: response.status,
              message: errorData.message
            },
          })
        )
        // throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.message}`);
        return errorData;
      }
      return response.json();

    } catch (error) {
      throw new Error(error.message)
    }

  }
  async getHtml(url, config = { mode: "no-cors" }) {
    console.log(url);

    const response = await fetch(url, config);
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
        console.log(errorData)
      } catch {

        errorData = { message: response.statusText };
      }

      document.dispatchEvent(
        new CustomEvent('error-received', {
          detail: {
            status: response.status,
            message: errorData.message
          },
        })
      )
      return errorData;
    }
    return await response.text();
  }
  get(endpoint, options = {}) {
    try {
      return this.request('GET', endpoint, options);

    } catch (error) {
      console.log(error)
    }
  }

  post(endpoint, body, options = {}) {
    return this.request('POST', endpoint, { ...options, body });
  }

  put(endpoint, body, options = {}) {
    return this.request('PUT', endpoint, { ...options, body });
  }

  patch(endpoint, body, options = {}) {
    return this.request('PATCH', endpoint, { ...options, body });
  }

  delete(endpoint, body, options = {}) {
    return this.request('DELETE', endpoint, { ...options, body });
  }
  copy(endpoint, body = {}, options = {}) {
    return this.request('COPY', endpoint, { ...options, body });
  }
}
export default API
export const api = new API("/api", null)
