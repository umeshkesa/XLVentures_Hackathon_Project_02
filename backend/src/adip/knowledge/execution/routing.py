"""Domain-Aware Routing — prepared for activation in future phases.

Architecture preparation only. No implementation.

When activated, KnowledgeDomain will drive:
  • Routing — each domain maps to a domain-specific index subset
  • Caching — domain-partitioned cache namespaces
  • Policies — domain-specific limits and allowed types
  • Retrieval — domain-scoped query execution
  • Index selection — domain-optimised embedding providers

Design:

    DomainConfig:
      index_manager: IndexManager     # domain-specific index
      cache: KnowledgeCache           # domain-partitioned cache
      policy_overrides: dict          # domain-specific policy rules
      embedding_model: str            # domain-optimised provider

    _domain_configs: dict[KnowledgeDomain, DomainConfig] = {}

    def get_domain_config(domain: KnowledgeDomain) -> DomainConfig:
        return self._domain_configs.get(domain, _default_config)

Integration point: KnowledgeCoordinator.retrieve() would call
get_domain_config(query.domains[0]) to retrieve domain-scoped
components before dispatching the retrieval strategy.

Future work:
  1. Define DomainConfig model
  2. Implement domain registry
  3. Wire domain configs into coordinator
  4. Expose domain routing via KnowledgeService
"""

from __future__ import annotations
