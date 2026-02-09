/**
 * Google Workspace + Google Maps API
 * Script completo para integración desde servidor externo
 *
 * Servicios soportados:
 * - Gmail: Leer, enviar, buscar
 * - Sheets: Leer, escribir, actualizar
 * - Docs: Crear, leer
 * - Drive: Listar, crear, compartir
 * - Slides: Crear presentaciones
 * - Keep: Crear notas (limitado)
 * - Maps: Geocoding, Distance, Directions
 */

// =============================================
// CONFIGURACIÓN
// =============================================

const CONFIG = {
  // IDs de recursos (actualizar con tus IDs)
  SHEETS: {
    // Crea una hoja y copia su ID de la URL
    DEFAULT_ID: 'TU_SHEET_ID_AQUI'
  },
  DRIVE: {
    // Folder ID opcional para guardar archivos
    DEFAULT_FOLDER_ID: 'TU_FOLDER_ID_AQUI'
  }
};

// =============================================
// WEB API - HANDLER PRINCIPAL
// =============================================

/**
 * Maneja requests GET - Para pruebas simples
 */
function doGet(e) {
  return jsonResponse({
    status: 'ok',
    message: 'Google Workspace API funcionando',
    timestamp: new Date().toISOString(),
    available_actions: [
      'gmail_list', 'gmail_send', 'gmail_search',
      'sheets_read', 'sheets_write', 'sheets_append',
      'docs_create', 'docs_read',
      'drive_list', 'drive_create',
      'slides_create',
      'maps_geocode', 'maps_distance', 'maps_route',
      'keep_create'
    ],
    usage: 'Usa POST con JSON body',
    example: {
      service: 'gmail',
      action: 'list',
      params: { max: 10 }
    }
  });
}

/**
 * Maneja requests POST - API principal
 * @param {Object} e - Evento con postData
 */
function doPost(e) {
  try {
    // Parsear body
    const params = JSON.parse(e.postData.contents);

    // Validar servicio y acción
    if (!params.service || !params.action) {
      return errorResponse('Faltan parámetros: service y action son requeridos');
    }

    // Router principal
    const result = routeRequest(params);

    return jsonResponse(result);

  } catch (error) {
    return errorResponse('Error: ' + error.toString());
  }
}

// =============================================
// ROUTER - DISTRIBUIDOR DE SERVICIOS
// =============================================

/**
 * Enruta la petición al servicio correspondiente
 */
function routeRequest(params) {
  const service = params.service.toLowerCase();
  const action = params.action.toLowerCase();

  // GMAIL
  if (service === 'gmail') {
    switch (action) {
      case 'list': return gmailList(params.max || 10);
      case 'send': return gmailSend(params);
      case 'search': return gmailSearch(params.query);
      case 'read': return gmailRead(params.id);
      default: return { error: 'Acción Gmail no encontrada: ' + action };
    }
  }

  // SHEETS
  if (service === 'sheets') {
    switch (action) {
      case 'read': return sheetsRead(params.sheetId, params.range);
      case 'write': return sheetsWrite(params.sheetId, params.range, params.values);
      case 'append': return sheetsAppend(params.sheetId, params.data);
      case 'create': return sheetsCreate(params.title, params.data);
      default: return { error: 'Acción Sheets no encontrada: ' + action };
    }
  }

  // DOCS
  if (service === 'docs') {
    switch (action) {
      case 'create': return docsCreate(params.title, params.content);
      case 'read': return docsRead(params.id);
      default: return { error: 'Acción Docs no encontrada: ' + action };
    }
  }

  // DRIVE
  if (service === 'drive') {
    switch (action) {
      case 'list': return driveList(params.query, params.max);
      case 'create': return driveCreate(params.name, params.type, params.content);
      case 'share': return driveShare(params.id, params.email);
      default: return { error: 'Acción Drive no encontrada: ' + action };
    }
  }

  // SLIDES
  if (service === 'slides') {
    switch (action) {
      case 'create': return slidesCreate(params.title, params.content);
      default: return { error: 'Acción Slides no encontrada: ' + action };
    }
  }

  // MAPS
  if (service === 'maps') {
    switch (action) {
      case 'geocode': return mapsGeocode(params.address);
      case 'distance': return mapsDistance(params.origin, params.destination);
      case 'route': return mapsRoute(params.origin, params.destination);
      case 'static': return mapsStatic(params.center, params.zoom);
      default: return { error: 'Acción Maps no encontrada: ' + action };
    }
  }

  // KEEP (Limitado)
  if (service === 'keep') {
    switch (action) {
      case 'create': return keepCreate(params.title, params.content);
      default: return { error: 'Acción Keep no encontrada: ' + action };
    }
  }

  return { error: 'Servicio no encontrado: ' + service };
}

// =============================================
// GMAIL
// =============================================

/**
 * Lista emails recientes
 */
function gmailList(maxResults) {
  const threads = GmailApp.getInboxThreads(0, maxResults);
  const emails = threads.map(thread => {
    const message = thread.getMessages()[0];
    return {
      id: thread.getId(),
      subject: message.getSubject(),
      from: message.getFrom(),
      date: message.getDate().toISOString(),
      body: message.getPlainBody().substring(0, 200) + '...'
    };
  });

  return {
    service: 'gmail',
    action: 'list',
    count: emails.length,
    data: emails
  };
}

/**
 * Envía un email
 */
function gmailSend(params) {
  GmailApp.sendEmail(
    params.to,
    params.subject || 'Sin asunto',
    params.body || '',
    {
      htmlBody: params.html,
      name: 'Google Workspace API',
      attachments: params.attachments || []
    }
  );

  return {
    service: 'gmail',
    action: 'send',
    success: true,
    to: params.to,
    subject: params.subject
  };
}

/**
 * Busca emails
 */
function gmailSearch(query) {
  const threads = GmailApp.search(query);
  const results = threads.slice(0, 20).map(thread => ({
    id: thread.getId(),
    subject: thread.getFirstMessageSubject(),
    messageCount: thread.getMessageCount()
  }));

  return {
    service: 'gmail',
    action: 'search',
    query: query,
    count: results.length,
    data: results
  };
}

/**
 * Lee un email específico
 */
function gmailRead(messageId) {
  const message = GmailApp.getMessageById(messageId);
  if (!message) {
    return { error: 'Mensaje no encontrado' };
  }

  return {
    service: 'gmail',
    action: 'read',
    data: {
      id: messageId,
      subject: message.getSubject(),
      from: message.getFrom(),
      to: message.getTo(),
      date: message.getDate().toISOString(),
      body: message.getPlainBody(),
      html: message.getHtmlBody()
    }
  };
}

// =============================================
// SHEETS
// =============================================

/**
 * Lee datos de una hoja
 */
function sheetsRead(sheetId, range) {
  const sheet = SpreadsheetApp.openById(sheetId);
  const data = sheet.getRange(range || 'A1').getValues();

  return {
    service: 'sheets',
    action: 'read',
    range: range || 'A1',
    data: data
  };
}

/**
 * Escribe datos en una hoja
 */
function sheetsWrite(sheetId, range, values) {
  const sheet = SpreadsheetApp.openById(sheetId);
  sheet.getRange(range).setValues(values);

  return {
    service: 'sheets',
    action: 'write',
    success: true,
    range: range,
    cellsUpdated: values.length * values[0].length
  };
}

/**
 * Agrega una fila a una hoja
 */
function sheetsAppend(sheetId, rowData) {
  const sheet = SpreadsheetApp.openById(sheetId);
  sheet.appendRow(rowData);

  return {
    service: 'sheets',
    action: 'append',
    success: true,
    data: rowData
  };
}

/**
 * Crea una nueva hoja de cálculo
 */
function sheetsCreate(title, initialData) {
  const sheet = SpreadsheetApp.create(title);

  if (initialData && initialData.length > 0) {
    sheet.getSheets()[0].getRange(1, 1, initialData.length, initialData[0].length)
      .setValues(initialData);
  }

  return {
    service: 'sheets',
    action: 'create',
    success: true,
    id: sheet.getId(),
    url: sheet.getUrl()
  };
}

// =============================================
// DOCS
// =============================================

/**
 * Crea un documento
 */
function docsCreate(title, content) {
  const doc = DocumentApp.create(title);
  const body = doc.getBody();

  if (content) {
    body.setText(content);
  }

  doc.saveAndClose();

  return {
    service: 'docs',
    action: 'create',
    success: true,
    id: doc.getId(),
    url: doc.getUrl()
  };
}

/**
 * Lee un documento
 */
function docsRead(docId) {
  const doc = DocumentApp.openById(docId);
  const body = doc.getBody();

  return {
    service: 'docs',
    action: 'read',
    id: docId,
    title: doc.getName(),
    content: body.getText()
  };
}

// =============================================
// DRIVE
// =============================================

/**
 * Lista archivos en Drive
 */
function driveList(query, maxResults) {
  const files = DriveApp.searchFiles(query || '');
  const results = [];

  let count = 0;
  while (files.hasNext() && count < (maxResults || 20)) {
    const file = files.next();
    results.push({
      id: file.getId(),
      name: file.getName(),
      type: file.getMimeType(),
      url: file.getUrl(),
      size: file.getSize()
    });
    count++;
  }

  return {
    service: 'drive',
    action: 'list',
    count: results.length,
    data: results
  };
}

/**
 * Crea un archivo en Drive
 */
function driveCreate(name, type, content) {
  let file;

  switch (type) {
    case 'document':
      file = DocumentApp.create(name);
      break;
    case 'spreadsheet':
      file = SpreadsheetApp.create(name);
      break;
    case 'folder':
      file = DriveApp.createFolder(name);
      break;
    default:
      // Archivo de texto
      file = DriveApp.createFile(name, content || '', MimeType.PLAIN_TEXT);
  }

  return {
    service: 'drive',
    action: 'create',
    success: true,
    id: file.getId(),
    url: file.getUrl(),
    name: name
  };
}

/**
 * Comparte un archivo
 */
function driveShare(fileId, email) {
  const file = DriveApp.getFileById(fileId);
  file.addEditor(email);

  return {
    service: 'drive',
    action: 'share',
    success: true,
    file: file.getName(),
    sharedWith: email
  };
}

// =============================================
// SLIDES
// =============================================

/**
 * Crea una presentación
 */
function slidesCreate(title, content) {
  const presentation = SlidesApp.create(title);

  if (content && content.length > 0) {
    const slides = presentation.getSlides();
    const firstSlide = slides[0];

    content.forEach(item => {
      if (item.type === 'text') {
        firstSlide.insertTextBox(item.text);
      }
    });
  }

  return {
    service: 'slides',
    action: 'create',
    success: true,
    id: presentation.getId(),
    url: presentation.getUrl()
  };
}

// =============================================
// MAPS
// =============================================

/**
 * Geocoding: Dirección → Coordenadas
 */
function mapsGeocode(address) {
  const response = Maps.newGeocoder()
    .setLanguage('es')
    .geocode(address);

  if (response.status === 'OK') {
    const result = response.results[0];
    return {
      service: 'maps',
      action: 'geocode',
      success: true,
      address: result.formatted_address,
      location: {
        lat: result.geometry.location.lat,
        lng: result.geometry.location.lng
      },
      viewport: result.geometry.viewport
    };
  }

  return {
    service: 'maps',
    action: 'geocode',
    success: false,
    error: 'No se encontró la dirección'
  };
}

/**
 * Distance Matrix: Distancia entre puntos
 */
function mapsDistance(origin, destination) {
  const response = Maps.newDistanceMatrix()
    .setOrigins(origin)
    .setDestinations(destination)
    .get();

  if (response.rows[0].elements[0].status === 'OK') {
    const element = response.rows[0].elements[0];
    return {
      service: 'maps',
      action: 'distance',
      success: true,
      origin: origin,
      destination: destination,
      distance: {
        text: element.distance.text,
        value: element.distance.value
      },
      duration: {
        text: element.duration.text,
        value: element.duration.value
      }
    };
  }

  return {
    service: 'maps',
    action: 'distance',
    success: false,
    error: 'No se pudo calcular la distancia'
  };
}

/**
 * Directions: Ruta óptima
 */
function mapsRoute(origin, destination) {
  const directions = Maps.newDirectionFinder()
    .setOrigin(origin)
    .setDestination(destination)
    .setMode(Maps.DirectionFinder.Mode.DRIVING)
    .getDirections();

  if (directions.routes.length > 0) {
    const route = directions.routes[0];
    const leg = route.legs[0];

    return {
      service: 'maps',
      action: 'route',
      success: true,
      summary: route.summary,
      distance: leg.distance.text,
      duration: leg.duration.text,
      steps: leg.steps.map(step => ({
        instruction: step.html_instructions.replace(/<[^>]*>/g, ''),
        distance: step.distance.text,
        duration: step.duration.text
      }))
    };
  }

  return {
    service: 'maps',
    action: 'route',
    success: false,
    error: 'No se pudo calcular la ruta'
  };
}

/**
 * Static Map URL (requiere API key para uso real)
 */
function mapsStatic(center, zoom) {
  // Nota: Esto requiere API Key de Google Maps Static API
  const apiKey = 'TU_API_KEY_AQUI'; // Configurar en Google Cloud

  const url = `https://maps.googleapis.com/maps/api/staticmap?` +
    `center=${encodeURIComponent(center)}&` +
    `zoom=${zoom || 13}&` +
    `size=600x400&` +
    `key=${apiKey}`;

  return {
    service: 'maps',
    action: 'static',
    url: url,
    note: 'Requiere API Key de Google Maps Static API'
  };
}

// =============================================
// KEEP (Limitado - usa Gmail como workaround)
// =============================================

/**
 * Crea una nota en Keep (envía email a keep@m.google.com)
 */
function keepCreate(title, content) {
  const email = title + '\n\n' + (content || '');

  GmailApp.sendEmail(
    'keep@m.google.com',  // Email de Keep
    title || 'Nota desde API',
    email,
    {
      name: 'Google Workspace API'
    }
  );

  return {
    service: 'keep',
    action: 'create',
    success: true,
    note: 'Nota creada via email a Keep',
    title: title
  };
}

// =============================================
// UTILIDADES
// =============================================

/**
 * Retorna una respuesta JSON exitosa
 */
function jsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Retorna una respuesta de error
 */
function errorResponse(message) {
  return jsonResponse({
    success: false,
    error: message,
    timestamp: new Date().toISOString()
  });
}

/**
 * Test rápido de todos los servicios
 */
function testAllServices() {
  const results = {
    timestamp: new Date().toISOString(),
    tests: []
  };

  // Test Gmail - Listar
  try {
    const emails = GmailApp.getInboxThreads(0, 1);
    results.tests.push({ service: 'gmail', action: 'list', status: 'ok' });
  } catch (e) {
    results.tests.push({ service: 'gmail', action: 'list', status: 'error', message: e.toString() });
  }

  // Test Sheets - Crear test
  try {
    const testSheet = SpreadsheetApp.create('API Test Sheet');
    results.tests.push({ service: 'sheets', action: 'create', status: 'ok', id: testSheet.getId() });
  } catch (e) {
    results.tests.push({ service: 'sheets', action: 'create', status: 'error', message: e.toString() });
  }

  // Test Maps - Geocoding
  try {
    const geo = Maps.newGeocoder().geocode('Buenos Aires, Argentina');
    results.tests.push({ service: 'maps', action: 'geocode', status: 'ok' });
  } catch (e) {
    results.tests.push({ service: 'maps', action: 'geocode', status: 'error', message: e.toString() });
  }

  return results;
}
