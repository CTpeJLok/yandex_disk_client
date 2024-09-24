document.querySelector('#form').addEventListener('submit', () => {
  const url = document.querySelector('input[name="url"]').value
  const key = document.querySelector('input[name="key"]').value

  const params = new URLSearchParams({ url: url, key: key })

  window.location.href = `?${params.toString()}`
})

document.querySelectorAll('.download-btn').forEach((btn) => {
  btn.addEventListener('click', async () => {
    const url = btn.getAttribute('data-url')
    const filename = btn.getAttribute('data-filename')

    const response = await fetch('/download/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        files: [
          {
            url: url,
            filename: filename,
          },
        ],
      }),
    })

    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = downloadUrl
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
  })
})

let toDownload = []
document.querySelectorAll('.select-file').forEach((input) => {
  input.addEventListener('change', () => {
    if (input.checked)
      toDownload = [
        ...toDownload,
        {
          url: input.getAttribute('data-url'),
          filename: input.getAttribute('data-filename'),
        },
      ]
    else
      toDownload = toDownload.filter(
        (file) => file.filename !== input.getAttribute('data-filename')
      )

    console.log(toDownload)
  })
})

document.querySelector('#download-all').addEventListener('click', async () => {
  if (!toDownload.length) return

  const response = await fetch('/download/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      files: toDownload,
    }),
  })

  const blob = await response.blob()
  const downloadUrl = window.URL.createObjectURL(new Blob([blob]))
  const link = document.createElement('a')
  link.href = downloadUrl
  link.setAttribute('download', 'files.zip')
  document.body.appendChild(link)
  link.click()
})
