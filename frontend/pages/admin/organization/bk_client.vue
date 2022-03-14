<template>
  <p v-if="$fetchState.pending">Fetching data ...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
  <div v-else>
    <div class="ma-3">
      <h3>Create Client</h3>
      <form @submit.prevent="createClient">
        <div class="mb-3">
          <v-text-field
            label="Name"
            v-model="name"
            :error-messages="nameErrors"
            required
            @blur="$v.name.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="CNPJ"
            v-model="cnpj"
            required
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Client code"
            v-model="client_code"
            :error-messages="clientCodeErrors"
            required
            @blur="$v.client_code.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Client code"
            v-model="client_code"
            required
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Vendor code"
            v-model="vendor_code"
            required
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Note"
            v-model="note"
          />
        </div>
        <h5>Status da empresa</h5>
        <v-radio-group v-model="status" style="width: 25%;">
          <v-radio
            label="Ativado"
            value="A"
          ></v-radio>
          <v-radio
            label="Desativado"
            value="D"
          ></v-radio>
          <v-radio
            label="Bloqueado"
            value="B"
          ></v-radio>
        </v-radio-group>
        <h5>Tipo de empresa</h5>
        <v-radio-group v-model="client_type" style="width: 25%;">
          <v-radio
            v-if="isAdmin()"
            label="Contratante"
            value="C"
          ></v-radio>
          <v-radio
            v-if="isAdmin() || isAdminAgent() || haveCreateClientPermissions()"
            label="Distribuidora"
            value="D"
          ></v-radio>
          <v-radio
            v-if="isAdmin() || isAdminAgent() || haveCreateClientPermissions()"
            label="Logista"
            value="L"
          ></v-radio>
          <v-radio
            v-if="isAdmin() || isAdminAgent() || haveCreateClientPermissions()"
            label="Outros"
            value="O"
          ></v-radio>
        </v-radio-group>
        <v-btn
          color="primary"
          type="submit"
          :loading="loading"
          :disabled="loading"
          >Submit</v-btn
        >
      </form>

      <h3 class="mt-6">Edit Client</h3>
      <v-data-table
        :headers="headers"
        :items="clients"
        :items-per-page="10"
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <client-edit-menu :client="item" @client-deleted="deleteClient(item)" />
        </template>
      </v-data-table>
    </div>
  </div>
</template>

<script>
import {
  required,
  maxLength,
  alphaNum,
  integer
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";

export default {
  middleware: ["authenticated"],
  components: {
    "client-edit-menu": require("@/components/admin/organization/client-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      name: null,
      cnpj: null,
      client_code: null,
      status: null,
      client_type: null,
      company_code: null,
      vendor_code: null,
      note: null,
      loading: false,
      clients: [],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'CNPJ', value: 'cnpj' },
        { text: 'Client code', value: 'client_code' },
        { text: 'Status', value: 'status' },
        { text: 'Client type', value: 'client_type' },
        { text: 'Price Table', value: 'price_table' },
        { text: 'Company code', value: 'company_code' },
        { text: 'Vendor code', value: 'vendor_code' },
        { text: 'Note', value: 'note' },
        { text: 'Actions', value: 'actions' },
      ]
    };
  },

  async fetch() {
    let clients = await this.$store.dispatch("organization/fetchClients");
    for (const client_index in clients){
      let client = clients[client_index]
      /** this.clients.push({name: client.name, cnpj: client.cnpj, client_code: client.client_code, */
        /** status: client.status, client_type: client.client_type, price_table: client.price_table}) */
    /** } */
      this.clients.push(client)
    }
  },

  validations: {
    name: { 
      required, 
      alphaNum, 
      maxLength: maxLength(12)
    },
    client_code: {
      required, 
      integer
    },
    clientInfoGroup: [
      "name",
      /** "cnpj", */
      "client_code",
      /** "status", */
      /** "client_type", */
      /** "client_code", */
    ],
  },

  computed: {
    nameErrors() {
      const errors = [];
      if (!this.$v.name.$dirty) return errors;
      !this.$v.name.alphaNum && errors.push("Must have only alphanumeric characters.");
      !this.$v.name.required && errors.push("Name is required");
      !this.$v.name.maxLength && errors.push("This field must have up to 12 characters.");
      return errors;
    },
    clientCodeErrors() {
      const errors = [];
      if (!this.$v.client_code.$dirty) return errors;
      !this.$v.name.alphaNum && errors.push("Must have only alphanumeric characters.");
      !this.$v.client_code.required && errors.push("Client code required");
      return errors;
    },
    companyCodeErrors() {
      const errors = [];
      if (!this.$v.client_code.$dirty) return errors;
      !this.$v.name.alphaNum && errors.push("Must have only alphanumeric characters.");
      !this.$v.client_code.required && errors.push("Client code required");
      return errors;
    },
    /** cpfErrors() {  */
      /** const errors = []; */
      /** if (!this.$v.cpf.$dirty) return errors; */
      /** !this.$v.cpf.required && errors.push("CPF is required."); */
      /** !this.$v.cpf.maxLength && errors.push("This field must have up to 14 characters."); */
      /** return errors; */
    /** }, */
  },

  methods: {
    async createClient() {
      this.$v.clientInfoGroup.$touch();
      if (this.$v.clientInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: "Please fill the form correctly.", alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("organization/createClient", {
          name: this.name, 
          cnpj: this.cnpj,
          client_code: this.client_code,
          status: this.status,
          client_type: this.client_type,
          client_code: this.client_code,
          vendor_code: this.vendor_code,
          note: this.note
        });
        if (data) {
          this.clients.push(data);
        }
        this.loading = false;
      }
    },
    deleteClient(clientToDelete) {
      this.clients = this.clients.filter((client) => client.client_code != clientToDelete.client_code);
    },
    haveCreateClientPermissions(){
			let user = this.$store.state.user.currentUser;
      if (user.permissions.includes("create_client" )){return true}
    },
    isAdmin(){
			let user = this.$store.state.user.currentUser;
      if (user.roles.includes("admin")) {return true}
    },
    isAdminAgent(){
			let user = this.$store.state.user.currentUser;
      if (user.roles.includes("admin_agent")) {return true}
    }
  },
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
