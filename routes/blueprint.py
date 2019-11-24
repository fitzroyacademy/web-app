from flask import Blueprint


class SubdomainBlueprint(Blueprint):
    def subdomain_route(self, rule, **options):
        """
        Like :meth:`Blueprint.route` but with additional rule for a subdomain.
        """

        def decorator(f):
            endpoint = options.pop("endpoint", f.__name__)
            self.add_url_rule(rule, endpoint, f, **options)
            self.add_url_rule(rule, endpoint, f, subdomain="<institute>", **options)

            return f

        return decorator
