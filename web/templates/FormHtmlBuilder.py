def FormInput(content: str, classes: str = ""):
    return F"""
        <div class="form-input input-group {classes}">
            {content}
        </div>
        """

class FormHtmlBuilder:
    def Form(content: str, classes: str = ""):
        return F"""
            <form method="post" class="form container {classes}">
                {content}
            </form>
            """

    def Password(text: str, name: str, id: str, classes: str = ""):
        return FormInput(F"""
            <label for="{name}" class="form-label">{text}:</label>
            <input type="password" name="{name}" id="{id}" class="form-control {classes}">
            """, classes="input-password"
        )

    def Submit(text: str, id: str, classes: str = ""):
        return F"""
            <button type="submit" class="btn btn-submit {classes}">{text}</button>
                """