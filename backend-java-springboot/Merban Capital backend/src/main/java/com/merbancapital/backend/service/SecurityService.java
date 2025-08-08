package com.merbancapital.backend.service;

import com.merbancapital.backend.model.Document;
import com.merbancapital.backend.security.UserPrincipal;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

@Component("securityService")
public class SecurityService {

    /**
     * Returns true if the currently authenticated user can access/download the given document.
     */
    public boolean canAccessDocument(Authentication authentication, Document doc) {
        if (authentication == null || !authentication.isAuthenticated()) {
            return false;
        }

        Object principalObj = authentication.getPrincipal();
        if (!(principalObj instanceof UserPrincipal principal)) {
            return false;
        }

        // Admins can see everything
        if (principal.getRoles().contains("ROLE_ADMIN")) {
            return true;
        }

        // Department users only see docs from their own department
        Long userDeptId = principal.getDepartmentId();
        return userDeptId != null && userDeptId.equals(doc.getDepartmentId());
    }
}
