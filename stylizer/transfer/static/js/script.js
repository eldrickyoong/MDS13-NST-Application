/**
 * ========== Init ==========
 */
window.addEventListener('DOMContentLoaded', () => {
  loadStyleThumbnails()

  setupUploadCard({
    areaId: 'content-upload',
    dropAreaSelectorId: 'content-box'
  })

  setupUploadCard({
    areaId: 'style-upload',
    dropAreaSelectorId: 'style-box'
  })

  document.getElementById('content-box').addEventListener('click', e => {
    resetUpload('content')
  })

  document.getElementById('style-box').addEventListener('click', e => {
    resetUpload('style')
  })
})

/**
 * ========== Upload Function ==========
 */

function setupUploadCard ({ areaId, dropAreaSelectorId }) {
  const input = document.getElementById(areaId)
  const dropArea = document.getElementById(dropAreaSelectorId)
  const type = areaId.includes('style') ? 'style' : 'content'

  // click listener
  dropArea.addEventListener('click', e => {
    // If an image is present, clicking the box should REMOVE it,
    // and must NOT open the file picker.
    if (dropArea.classList.contains('has-image')) {
      e.preventDefault()
      e.stopImmediatePropagation() // prevent any other click handlers on this node
      resetUpload(type)
      return // <- do NOT call input.click()
    }

    input.click()
  })

  dropArea.addEventListener('drop', e => {
    e.preventDefault()
    dropArea.classList.remove('dragover')
    const file = e.dataTransfer.files[0]
    if (!file) return
    input.files = e.dataTransfer.files
    showPreview(file, type)
  })

  // Input change
  input.addEventListener('change', () => {
    if (!input.files.length) return
    showPreview(input.files[0], type)
  })
}

// -- Reset Upload Logic ---
function resetUpload (type) {
  document.getElementById(`${type}-upload`).value = ''
  document.getElementById(`upload-${type}-display`).style.display = 'flex'
  document.getElementById(`preview-image-${type}`).src = ''
  document.getElementById(`preview-container-${type}`).style.display = 'none'

  // remove overlay trigger
  document.getElementById(`${type}-box`).classList.remove('has-image')
  checkImagesReady()
}

/**
 * ========== Style Thumbnails ==========
 */
function loadStyleThumbnails () {
  const gallery = document.getElementById('style-gallery')
  gallery.innerHTML = ''

  // Static path to predefined styles
  const basePath = '/static/images/johnson_fast_style/'

  // List of image filenames
  const styleImages = [
    'anime.jpg',
    'bw_drawing.jpg',
    'candy.jpg',
    'cartoon_artstyle.jpg',
    'children_book_illustration.jpg',
    'chinese_painting.jpg',
    'cubism.jpg',
    'dreamscape.jpg',
    'edtaonisl.jpg',
    'fantasy_world.jpg',
    'graffiti.jpg',
    'japanese_painting.jpg',
    'marvel_comic.jpg',
    'mosaic.jpg',
    'nouveau.jpg',
    'papercraft.jpg',
    'pixel_art.jpg',
    'pyschedelic.jpg',
    'starry.jpg',
    'steampunk.jpg',
    'tiles.jpg',
    'tribal_art.jpg'
  ]

  styleImages.forEach(fileName => {
    const img = document.createElement('img')
    img.src = basePath + fileName
    img.classList.add('style-thumb')

    img.addEventListener('click', () => {
      document
        .querySelectorAll('.style-thumb')
        .forEach(el => el.classList.remove('selected'))
      img.classList.add('selected')
      const customInput = document.getElementById('style-upload')
      customInput.value = ''
      showPreview(img.src, 'style')
      const predefinedInput = document.getElementById('selected-style-path')
      predefinedInput.value = img.src
    })

    gallery.appendChild(img)
  })
}

/**
 * Checks whether both content and style images are uploaded.
 * Adds or removes the `.ready` flag on the result container.
 */
function checkImagesReady () {
  const contentReady = document
    .getElementById('content-box')
    .classList.contains('has-image')
  const styleReady = document
    .getElementById('style-box')
    .classList.contains('has-image')
  const resultContainer = document.getElementById('result-container')

  if (contentReady && styleReady) {
    resultContainer.classList.add('ready')
  } else {
    resultContainer.classList.remove('ready')
  }
}

// --- Preview Logic ---
function showPreview (input, type) {
  const previewId = `preview-image-${type}`
  const label = document.getElementById(`upload-${type}-display`)
  const container = document.getElementById(`preview-container-${type}`)
  const dropAreaSelectorId = `${type}-box`

  const img = document.getElementById(previewId)

  const setImage = src => {
    if (img) img.src = src
    img.style.display = 'block'
    if (label) label.style.display = 'none'
    if (container) container.style.display = 'flex'
  }

  if (typeof input === 'string') {
    // input is a URL
    setImage(input)
  } else {
    // input is a File
    const reader = new FileReader()
    reader.onload = e => setImage(e.target.result)
    reader.readAsDataURL(input)
  }

  // Show the overlay + mark as active
  document.getElementById(dropAreaSelectorId).classList.add('has-image')
  checkImagesReady()
}

function downloadResult () {
  const img = document.getElementById('preview-image-result')
  if (!img.src) {
    alert('No image to download yet!')
    return
  }

  const link = document.createElement('a')
  link.href = img.src
  link.download = 'stylized_image.png'
  link.click()
}

function showLoader () {
  const loader = document.getElementById('result-loader')
  if (loader) loader.classList.add('active')
}

function hideLoader () {
  const loader = document.getElementById('result-loader')
  if (loader) loader.classList.remove('active')
}

async function generateStylizedImage () {
  const resultContainer = document.getElementById('preview-container-result')
  const stylizedImg = document.getElementById('preview-image-result')
  const contentInput = document.getElementById('content-upload')
  const styleInput = document.getElementById('style-upload')
  const stylePath = document.getElementById('selected-style-path').value
  const resultBox = document.getElementById('result-inner-box')

  showLoader()

  const formData = new FormData()
  formData.append('content', contentInput.files[0])

  if (styleInput.files.length > 0) {
    formData.append('style', styleInput.files[0])
  } else if (stylePath) {
    formData.append('style_path', stylePath)
  } else {
    alert('Please upload a style image or choose one from the gallery.')
    return
  }

  try {
    const response = await fetch('/stylize/', {
      method: 'POST',
      body: formData
    })

    if (!response.ok) throw new Error('Stylization failed')

    const blob = await response.blob()
    const imageUrl = URL.createObjectURL(blob)

    stylizedImg.src = imageUrl
    stylizedImg.style.display = 'block'
    resultContainer.style.display = 'flex'
    resultBox.classList.add('has-image')

    hideLoader()
  } catch (error) {
    console.error('Error:', error)
    alert('There was a problem generating the stylized image.')
  }
}
