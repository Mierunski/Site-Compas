<template>
  <v-container class="fill-height">
    <v-responsive class="align-centerfill-height mx-auto" max-width="1200">
      <v-row>
        <v-col cols="12">
          <v-form @submit.prevent>
            <v-text-field
              v-model="url"
              :rules="rules"
              label="Website URL"
            ></v-text-field>
            <v-text-field
              v-model="Offering"
              :rules="rules"
              label="Your offering"
            ></v-text-field>
            <v-btn class="mt-2" type="submit"  @click="submit" block>Submit</v-btn>
          </v-form>
        </v-col>
      </v-row>
      <v-card v-html="output">
      </v-card>
    </v-responsive>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      listItems: [],
      users: [],
      day: "",
      date: "",
      url: "",
      output: "",
    };
  },
  methods: {
    async submit() {
      this.output = "Working...";
      
      const res = await fetch("http://127.0.0.1:5000/run_flow", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: this.url,
          offer: this.Offering,
        }),
      });
      const finalRes = await res.json();
      console.log(finalRes);
      this.output = finalRes;
    },
  },
};
</script>
