from typing import Annotated, List, Optional, Set
from fastapi import Depends, HTTPException, status

from backend.app.auth import RoleChecker
from backend.app.constants import POSSIBLE_ROLES_SET

# Role dependencies
def role_checker_dependency_factory(roles: Set[str]):
    roles_set={role.lower() for role in roles}
    
    is_subset=roles_set.issubset(POSSIBLE_ROLES_SET)
    if(not is_subset):
        raise ValueError(f"Invalid roles. Allowed roles: {POSSIBLE_ROLES_SET}")
    
    return Depends(RoleChecker(allowed_roles=roles))

# Permission dependencies
AdminDependency=role_checker_dependency_factory(['admin', 'user'])
UserDependency=role_checker_dependency_factory(['user'])