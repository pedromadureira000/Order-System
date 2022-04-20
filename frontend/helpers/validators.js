import { helpers} from "vuelidate/lib/validators";
export const slugFieldValidator = helpers.regex('alphaNumDashAndUnderline', /^[a-z\d-_]*$/i)
export const cnpjFieldValidator = helpers.regex('CNPJ', /^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$/)
export const raizcnpjFieldValidator = helpers.regex('RaizCNPJ', /^\d{2}\.\d{3}\.\d{3}$/)
// export const cpfFieldValidator = helpers.regex('CPF', /^\d{3}\.\d{3}\.\d{3}\-\d{2}$/)
export const moneyValidator = helpers.regex('moneyValidator', /^R\$\s[0-9]\d{0,2}(\.\d{3})*,\d{2}$/)

export const money = {
          decimal: ',',
          thousands: '.',
          prefix: 'R$ ',
          suffix: '',
          precision: 2,
          masked: false
        }

export const decimal_only_2places = helpers.regex('decimal_only_2places', /^(?!(?:0|0\.0|0\.00)$)[+]?\d+(\.\d[0-9]?)?$/)
