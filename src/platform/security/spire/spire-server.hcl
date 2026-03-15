server {
  bind_address = "0.0.0.0"
  bind_port    = "8081"
  trust_domain = "gaia.internal"
  data_dir     = "/opt/spire/data/server"
  log_level    = "INFO"
  ca_subject = {
    country       = ["US"]
    organization  = ["GAIA"]
    common_name   = "GAIA SPIRE CA"
  }
}

plugins {
  DataStore "sql" {
    plugin_data {
      database_type     = "sqlite3"
      connection_string = "/opt/spire/data/server/datastore.sqlite3"
    }
  }

  NodeAttestor "tpm_devid" {
    plugin_cmd  = "/opt/spire/plugins/spire-server-node-attestor-tpm"
    plugin_data {
      trust_on_first_use = true
    }
  }

  NodeAttestor "k8s_psat" {
    plugin_data {
      clusters = {
        "gaia-cluster" = {
          service_account_allow_list = ["spire:spire-agent"]
        }
      }
    }
  }

  KeyManager "disk" {
    plugin_data {
      keys_path = "/opt/spire/data/server/keys.json"
    }
  }

  UpstreamAuthority "disk" {
    plugin_data {
      cert_file_path   = "/opt/spire/conf/upstream_ca.crt"
      key_file_path    = "/opt/spire/conf/upstream_ca.key"
      bundle_file_path = "/opt/spire/conf/upstream_bundle.crt"
    }
  }
}
