document.querySelector('#form').addEventListener('submit', () => {
  const url = document.querySelector('input[name="url"]').value
  const key = document.querySelector('input[name="key"]').value

  const params = new URLSearchParams({ url: url, key: key })

  window.location.href = `?${params.toString()}`
})
