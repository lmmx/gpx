get_projects_query = """
query {
  viewer {
    id
    login
    name
    projectsV2(first: 100) {
      nodes {
        closed
        createdAt
        public
        number
        resourcePath
        title
        url
      }
      totalCount
    }
  }
}
"""

get_project_items_query = """
query($number: Int!) {
  viewer {
    projectV2(number: $number) {
      id
      title
      shortDescription
      items(first: 100) {
        nodes {
          id
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldTextValue {
                text
                field {
                  ... on ProjectV2FieldCommon {
                    name
                    dataType
                  }
                }
              }
              ... on ProjectV2ItemFieldDateValue {
                date
                field {
                  ... on ProjectV2FieldCommon {
                    name
                    dataType
                  }
                }
              }
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2FieldCommon {
                    name
                    dataType
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
