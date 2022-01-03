const middleware = {}

middleware['admin'] = require('../middleware/admin.js')
middleware['admin'] = middleware['admin'].default || middleware['admin']

middleware['auth'] = require('../middleware/auth.js')
middleware['auth'] = middleware['auth'].default || middleware['auth']

middleware['authenticated'] = require('../middleware/authenticated.js')
middleware['authenticated'] = middleware['authenticated'].default || middleware['authenticated']

middleware['fwdcookies'] = require('../middleware/fwdcookies.js')
middleware['fwdcookies'] = middleware['fwdcookies'].default || middleware['fwdcookies']

middleware['reports'] = require('../middleware/reports.js')
middleware['reports'] = middleware['reports'].default || middleware['reports']

export default middleware
