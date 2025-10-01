variable "VERSION" {
  default = "1.0.0"
}

variable "REPO_NAME" {
  default = "get-prompts"
}

group "default" {
  targets = ["gen404-get-prompts"]
}

target "gen404-get-prompts" {
  platforms  = ["linux/amd64"]
  context = "."
  dockerfile = "Dockerfile"
  tags = [
    "europe-docker.pkg.dev/gen-456515/${REPO_NAME}/${REPO_NAME}:${VERSION}",
  ]
}
