import { helpers} from "vuelidate/lib/validators";
export const slugFieldValidator = helpers.regex('alphaNumDashAndUnderline', /^[a-z\d-_]*$/i)
export const cnpjFieldValidator = helpers.regex('CNPJ', /^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$/)
export const raizcnpjFieldValidator = helpers.regex('RaizCNPJ', /^\d{2}\.\d{3}\.\d{3}$/)
// export const cpfFieldValidator = helpers.regex('CPF', /^\d{3}\.\d{3}\.\d{3}\-\d{2}$/)


