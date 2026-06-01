cube(`LeaseRiskCube`, {
  sql: `SELECT l.*, p.name FROM lease_expirations l JOIN properties p ON l.propertyid = p.id`,

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
    name: {
      sql: `name`,
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