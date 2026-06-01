cube(`LeaseRiskCube`, {
  sql: `SELECT * FROM lease_expirations`,

  measures: {
    monthlyRent: {
      sql: `monthlyrent`,
      type: `sum`,
      description: `Monthly lease exposure value`
    }
  },

  dimensions: {
    id: {
      sql: `id`,
      type: `string`,
      primaryKey: true
    },
    propertyId: {
      sql: `propertyid`,
      type: `string`
    },
    unitType: {
      sql: `unittype`,
      type: `string`
    },
    expirationDate: {
      sql: `expirationdate`,
      type: `string`
    }
  }
});